#!/usr/bin/env python3
"""
==============================================================================
Method 3: Python Client Library — Full End-to-End Pipeline
==============================================================================

WHAT THIS DOES:
  Uploads a conversation transcript to CX Insights, runs analysis with
  all annotators (including sentiment), and displays turn-by-turn
  sentiment results in a nicely formatted table.

HOW TO RUN:
  1. Make sure you ran 00_setup.sh first (APIs enabled, bucket created,
     sample_conversation.json uploaded to GCS)

  2. Install dependencies (if you said "y" during setup, this is already done):
       source venv/bin/activate
       pip install -r requirements.txt

  3. Authenticate (Cloud Shell does this automatically):
       gcloud auth application-default login

  4. Edit the 2 variables in the CONFIGURATION section below.
     EASIEST way — run these two commands (replace the values):
       sed -i 's/your-project-id/MY-ACTUAL-PROJECT-ID/g' method3_python_client.py
       sed -i 's/your-bucket-name/my-unique-bucket-12345/g' method3_python_client.py

     Or open in an editor:
       cloudshell edit method3_python_client.py   (Cloud Shell)
       nano method3_python_client.py              (terminal)

  5. Run:
       python method3_python_client.py

  6. (Optional) Run with flags:
       python method3_python_client.py --sentiment-only
       python method3_python_client.py --all-features
       python method3_python_client.py --bulk

==============================================================================
"""

import sys
import json
import argparse
from google.cloud import contact_center_insights_v1
from google.cloud import storage

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION — Edit these 3 values                                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝

PROJECT_ID = "your-project-id"        # <-- Your GCP project ID
LOCATION = "us-central1"              # <-- Region (us-central1 is most common)
BUCKET_NAME = "your-bucket-name"      # <-- Your GCS bucket name

# Derived (no need to edit)
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
GCS_TRANSCRIPT_URI = f"gs://{BUCKET_NAME}/transcripts/sample_conversation.json"


# ==============================================================================
# STEP 1: Upload transcript to Cloud Storage (optional)
# ==============================================================================

def step1_upload_to_gcs(local_file: str = "sample_conversation.json") -> str:
    """
    Upload a local JSON transcript file to Google Cloud Storage.
    Skip this if you already uploaded via 00_setup.sh.

    Args:
        local_file: Path to the local JSON file.

    Returns:
        The GCS URI (gs://...) of the uploaded file.
    """
    print("=" * 70)
    print("STEP 1: Upload transcript to Cloud Storage")
    print("=" * 70)

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_name = f"transcripts/{local_file.split('/')[-1]}"
    blob = bucket.blob(blob_name)

    print(f"  Uploading {local_file} to gs://{BUCKET_NAME}/{blob_name}...")
    blob.upload_from_filename(local_file)

    gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
    print(f"  Uploaded to: {gcs_uri}")
    print()
    return gcs_uri


# ==============================================================================
# STEP 2: Upload conversation to CX Insights
# ==============================================================================

def step2_upload_conversation(gcs_transcript_uri: str) -> str:
    """
    Upload a conversation to CX Insights.
    This creates a conversation resource and returns its full name.

    Args:
        gcs_transcript_uri: GCS path to the transcript JSON file.

    Returns:
        The conversation resource name (projects/.../conversations/...).
    """
    print("=" * 70)
    print("STEP 2: Upload conversation to CX Insights")
    print("=" * 70)
    print(f"  Transcript URI: {gcs_transcript_uri}")

    client = contact_center_insights_v1.ContactCenterInsightsClient()

    # Build the conversation object
    conversation = contact_center_insights_v1.Conversation()
    conversation.data_source.gcs_source.transcript_uri = gcs_transcript_uri
    conversation.medium = contact_center_insights_v1.Conversation.Medium.CHAT

    # Build the upload request
    request = contact_center_insights_v1.UploadConversationRequest(
        parent=PARENT,
        conversation=conversation,
    )

    print("  Uploading (this returns a long-running operation)...")
    operation = client.upload_conversation(request=request)

    print("  Waiting for upload to complete...")
    result = operation.result(timeout=600)  # 10 minute timeout

    print(f"  Conversation created: {result.name}")
    print()
    return result.name


# ==============================================================================
# STEP 3: Run analysis
# ==============================================================================

def step3_analyze_conversation(
    conversation_name: str,
    sentiment_only: bool = False,
) -> str:
    """
    Run analysis on a conversation.

    Args:
        conversation_name: Full resource name of the conversation.
        sentiment_only: If True, only run the sentiment annotator.
                        If False, run ALL annotators (default).

    Returns:
        The analysis resource name.
    """
    print("=" * 70)
    print("STEP 3: Analyze conversation")
    print("=" * 70)

    client = contact_center_insights_v1.ContactCenterInsightsClient()

    analysis = contact_center_insights_v1.Analysis()

    if sentiment_only:
        print("  Mode: Sentiment annotator ONLY")
        analysis.annotator_selector.run_sentiment_annotator = True
    else:
        print("  Mode: ALL annotators (sentiment, entity, intent, etc.)")
        # When annotator_selector is empty, ALL annotators run by default.
        # But you can also explicitly enable them:
        #
        # analysis.annotator_selector.run_sentiment_annotator = True
        # analysis.annotator_selector.run_entity_annotator = True
        # analysis.annotator_selector.run_intent_annotator = True
        # analysis.annotator_selector.run_silence_annotator = True
        # analysis.annotator_selector.run_interruption_annotator = True
        # analysis.annotator_selector.run_issue_model_annotator = True

    print("  Starting analysis (this may take 1-2 minutes)...")
    operation = client.create_analysis(
        parent=conversation_name,
        analysis=analysis,
    )

    result = operation.result(timeout=86400)
    print(f"  Analysis complete: {result.name}")
    print()
    return result.name


# ==============================================================================
# STEP 4: Retrieve and display results
# ==============================================================================

def step4_display_results(
    conversation_name: str,
    show_all_features: bool = True,
):
    """
    Retrieve the conversation with its latest analysis and display
    turn-by-turn sentiment + all other features.

    Args:
        conversation_name: Full resource name of the conversation.
        show_all_features: If True, display all annotation types.
    """
    print("=" * 70)
    print("STEP 4: Retrieve and display results")
    print("=" * 70)

    client = contact_center_insights_v1.ContactCenterInsightsClient()
    conversation = client.get_conversation(name=conversation_name)

    # ── 4a: Customer Sentiment Journey (HERO VISUAL) ────────────────────────
    print()
    print("\u2554" + "\u2550" * 68 + "\u2557")
    print("\u2551  CUSTOMER SENTIMENT JOURNEY" + " " * 40 + "\u2551")
    print("\u255a" + "\u2550" * 68 + "\u255d")
    print()

    _display_sentiment_journey(conversation)

    # ── 4b: Full Turn-by-Turn Detail ──────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  FULL TURN-BY-TURN DETAIL (All Speakers)" + " " * 26 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_turn_sentiment(conversation)

    # ── 4c: Conversation-Level Sentiment ───────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  CONVERSATION-LEVEL SENTIMENT" + " " * 38 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_conversation_sentiment(conversation)

    if not show_all_features:
        return

    # ── 4d: Entity Extraction ──────────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ENTITY EXTRACTION" + " " * 49 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_entities(conversation)

    # ── 4e: Intent Detection ───────────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  INTENT DETECTION" + " " * 50 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_intents(conversation)

    # ── 4f: Issue/Topic Detection ──────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ISSUE / TOPIC DETECTION" + " " * 43 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_issues(conversation)

    # ── 4g: All Annotations Summary ────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ALL ANNOTATIONS SUMMARY" + " " * 43 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_all_annotations(conversation)


def _display_turn_sentiment(conversation):
    """Display per-turn sentiment with visual bars and message text."""
    turns = _get_turns_with_sentiment(conversation)

    if not turns:
        print("  No turn data found. Run an analysis first.")
        return

    has_any_score = any(t["score"] is not None for t in turns)
    if not has_any_score:
        print("  No sentiment annotations found.")
        print("  (Run analysis first, then retrieve results.)")
        return

    has_text = any(t["text"] for t in turns)

    # Build display data
    rows = []
    for t in turns:
        score_str = f"{t['score']:+.2f}" if t["score"] is not None else "  N/A"
        mag_str = f"{t['magnitude']:.2f}" if t["magnitude"] is not None else " N/A"
        label = _get_sentiment_label(t["score"], t["magnitude"] or 0.0) if t["score"] is not None else ""
        bar = _sentiment_bar(t["score"]) if t["score"] is not None else "\u2591" * 20
        text = t["text"]
        if len(text) > 45:
            text = text[:42] + "..."
        rows.append({
            "Turn": t["turn"],
            "Speaker": t["role"],
            "Score": score_str,
            "Mag.": mag_str,
            "Bar": bar,
            "Label": label,
            "Text": text,
        })

    if HAS_TABULATE and has_text:
        print(tabulate(rows, headers="keys", tablefmt="rounded_grid"))
    elif HAS_TABULATE:
        simple_rows = [{k: v for k, v in r.items() if k != "Text"} for r in rows]
        print(tabulate(simple_rows, headers="keys", tablefmt="rounded_grid"))
    else:
        # Fallback: formatted output
        if has_text:
            print(f"  {'Turn':<5} {'Speaker':<9} {'Score':>6} {'Mag.':>5}  {'Bar':<20}  {'Label':<18} Message")
            print(f"  {'─' * 5} {'─' * 9} {'─' * 6} {'─' * 5}  {'─' * 20}  {'─' * 18} {'─' * 40}")
            for r in rows:
                print(f"  {r['Turn']:<5} {r['Speaker']:<9} {r['Score']:>6} {r['Mag.']:>5}  {r['Bar']:<20}  {r['Label']:<18} {r['Text']}")
        else:
            print(f"  {'Turn':<5} {'Speaker':<9} {'Score':>6} {'Mag.':>5}  {'Bar':<20}  {'Label'}")
            print(f"  {'─' * 5} {'─' * 9} {'─' * 6} {'─' * 5}  {'─' * 20}  {'─' * 18}")
            for r in rows:
                print(f"  {r['Turn']:<5} {r['Speaker']:<9} {r['Score']:>6} {r['Mag.']:>5}  {r['Bar']:<20}  {r['Label']}")


def _display_conversation_sentiment(conversation):
    """Display conversation-level sentiment."""
    if not conversation.latest_analysis:
        return

    metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata
    if not metadata or not metadata.sentiments:
        print("  No conversation-level sentiment data found.")
        return

    for sentiment in metadata.sentiments:
        role = "Customer" if sentiment.channel_tag == 1 else "Agent"
        score = sentiment.sentiment_data.score
        magnitude = sentiment.sentiment_data.magnitude
        label = _get_sentiment_label(score, magnitude)
        print(f"  {role:>10}: score={score:+.2f}, magnitude={magnitude:.2f}  [{label}]")


def _display_entities(conversation):
    """Display extracted entities."""
    metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata
    if not metadata or not metadata.entities:
        print("  No entities found.")
        return

    for name, entity_data in metadata.entities.items():
        sentiment_str = ""
        if entity_data.sentiment:
            sentiment_str = f" (sentiment: {entity_data.sentiment.score:+.2f})"
        print(f"  {name} [{entity_data.type_}]{sentiment_str}")


def _display_intents(conversation):
    """Display detected intents."""
    metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata
    if not metadata or not metadata.intents:
        print("  No intents detected.")
        return

    for name, intent_data in metadata.intents.items():
        print(f"  {name} (ID: {intent_data.id})")


def _display_issues(conversation):
    """Display detected issues/topics."""
    metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata
    if not metadata or not metadata.issue_model_result:
        print("  No issues detected (this requires a trained issue model).")
        return

    issues = metadata.issue_model_result.issues or []
    if not issues:
        print("  No issues detected.")
        return

    for issue in issues:
        print(f"  {issue.issue} (confidence: {issue.score:.2f})")


def _display_all_annotations(conversation):
    """Display a summary of all annotation types."""
    metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata
    if not metadata or not metadata.annotations:
        print("  No annotations found.")
        return

    type_counts = {
        "sentiment": 0,
        "entity_mention": 0,
        "intent_match": 0,
        "silence": 0,
        "interruption": 0,
        "other": 0,
    }

    for annotation in metadata.annotations:
        if annotation.sentiment_data:
            type_counts["sentiment"] += 1
        elif annotation.entity_mention_data:
            type_counts["entity_mention"] += 1
        elif annotation.intent_match_data:
            type_counts["intent_match"] += 1
        elif annotation.silence_data:
            type_counts["silence"] += 1
        elif annotation.interruption_data:
            type_counts["interruption"] += 1
        else:
            type_counts["other"] += 1

    total = sum(type_counts.values())
    print(f"  Total annotations: {total}")
    print()
    for annotation_type, count in type_counts.items():
        if count > 0:
            bar = "#" * count
            print(f"  {annotation_type:>16}: {count:>3}  {bar}")


def _get_sentiment_label(score: float, magnitude: float = 0.0) -> str:
    """Convert a sentiment score + magnitude to a human-readable label."""
    if score >= 0.75:
        return "POSITIVE"
    elif score >= 0.25:
        return "SOMEWHAT POSITIVE"
    elif score > -0.25:
        if magnitude > 0.5:
            return "MIXED"
        else:
            return "NEUTRAL"
    elif score > -0.75:
        return "SOMEWHAT NEGATIVE"
    else:
        return "NEGATIVE"


def _sentiment_bar(score, width=20):
    """Create a visual sentiment bar. Negative fills left, positive fills right."""
    if score is None:
        return "\u2591" * width  # ░ all light shade
    center = width // 2
    bar = list("\u2591" * width)  # ░ light shade background
    if score < 0:
        fill = min(center, max(1, round(abs(score) * center)))
        for i in range(center - fill, center):
            bar[i] = "\u2593"  # ▓ dark shade
    elif score > 0:
        fill = min(center, max(1, round(score * center)))
        for i in range(center, center + fill):
            bar[i] = "\u2588"  # █ full block
    return "".join(bar)


def _get_turns_with_sentiment(conversation):
    """
    Extract turns with text + sentiment from a conversation.
    Tries transcript segments first, falls back to annotations.
    Returns list of dicts with: turn, role, text, score, magnitude
    """
    segments = []
    if conversation.transcript and conversation.transcript.transcript_segments:
        segments = list(conversation.transcript.transcript_segments)

    result = conversation.latest_analysis.analysis_result if conversation.latest_analysis else None
    metadata = result.call_analysis_metadata if result else None
    annotations = [a for a in (metadata.annotations or []) if a.sentiment_data] if metadata else []

    turns = []
    has_segment_sentiment = False

    # Build turns from transcript segments
    for i, seg in enumerate(segments):
        channel = seg.channel_tag
        role = "CUSTOMER" if channel == 1 else "AGENT"
        text = seg.text or ""
        score = None
        magnitude = None
        if hasattr(seg, "sentiment") and seg.sentiment:
            score = seg.sentiment.score
            magnitude = seg.sentiment.magnitude
            has_segment_sentiment = True
        turns.append({
            "turn": i + 1, "role": role, "text": text,
            "score": score, "magnitude": magnitude,
        })

    # Fallback: match annotations to segments by transcript_index
    if not has_segment_sentiment and annotations and turns:
        ann_by_index = {}
        for ann in annotations:
            idx = None
            if hasattr(ann, "annotation_start_boundary") and ann.annotation_start_boundary:
                idx = ann.annotation_start_boundary.transcript_index
            if idx is not None:
                ann_by_index[idx] = ann
        if ann_by_index:
            for t in turns:
                ann = ann_by_index.get(t["turn"] - 1)
                if ann:
                    t["score"] = ann.sentiment_data.score
                    t["magnitude"] = ann.sentiment_data.magnitude
        else:
            # No index — pair by order
            for i, ann in enumerate(annotations):
                if i < len(turns):
                    turns[i]["score"] = ann.sentiment_data.score
                    turns[i]["magnitude"] = ann.sentiment_data.magnitude

    # Last resort: if no segments at all, build from annotations alone
    if not turns and annotations:
        for i, ann in enumerate(annotations):
            channel = ann.channel_tag
            turns.append({
                "turn": i + 1,
                "role": "CUSTOMER" if channel == 1 else "AGENT",
                "text": "",
                "score": ann.sentiment_data.score,
                "magnitude": ann.sentiment_data.magnitude,
            })

    return turns


def _display_sentiment_journey(conversation):
    """
    Hero visual: Customer sentiment journey with bars, arrows, and summary box.
    This is the main demo-friendly visualization.
    """
    turns = _get_turns_with_sentiment(conversation)
    customer_turns = [t for t in turns if t["role"] == "CUSTOMER" and t["score"] is not None]

    if not customer_turns:
        print("  No customer sentiment data available.")
        return

    # Header
    bar_legend = "\u2593" * 5 + " Negative    \u2591" * 0 + "Neutral    " + "\u2588" * 5 + " Positive"
    print(f"  Scale: {bar_legend}")
    print()
    print(f"  {'Turn':<8} {'Score':>6}  {'':─<20}  Message")
    print(f"  {'─' * 8} {'─' * 6}  {'─' * 20}  {'─' * 55}")

    for i, ct in enumerate(customer_turns):
        bar = _sentiment_bar(ct["score"])
        label = _get_sentiment_label(ct["score"], ct["magnitude"] or 0.0)
        # Truncate text for display
        text = ct["text"]
        if len(text) > 55:
            text = text[:52] + "..."
        print(f'  Turn {ct["turn"]:<3} {ct["score"]:>+6.2f}  {bar}  "{text}"')

        # Show arrow between customer turns
        if i < len(customer_turns) - 1:
            next_score = customer_turns[i + 1]["score"]
            diff = next_score - ct["score"]
            if diff > 0.3:
                arrow = "          \u2197 +"  # ↗
            elif diff < -0.3:
                arrow = "          \u2198 "   # ↘
            elif diff > 0:
                arrow = "          \u2192 +"  # →
            elif diff < 0:
                arrow = "          \u2192 "   # →
            else:
                arrow = "          \u2192  "  # →
            print(f"{arrow}{diff:.2f}")

    # Summary box
    first = customer_turns[0]["score"]
    last = customer_turns[-1]["score"]
    low = min(ct["score"] for ct in customer_turns)
    high = max(ct["score"] for ct in customer_turns)
    shift = last - first

    print()
    print(f"  \u250c{'─' * 62}\u2510")
    print(f"  \u2502  CUSTOMER SENTIMENT SUMMARY{' ' * 35}\u2502")
    print(f"  \u251c{'─' * 62}\u2524")
    print(f"  \u2502  Opening sentiment:  {first:>+6.2f}  ({_get_sentiment_label(first):<18}){' ' * 12}\u2502")
    print(f"  \u2502  Lowest point:       {low:>+6.2f}  ({_get_sentiment_label(low):<18}){' ' * 12}\u2502")
    print(f"  \u2502  Highest point:      {high:>+6.2f}  ({_get_sentiment_label(high):<18}){' ' * 12}\u2502")
    print(f"  \u2502  Closing sentiment:  {last:>+6.2f}  ({_get_sentiment_label(last):<18}){' ' * 12}\u2502")
    print(f"  \u251c{'─' * 62}\u2524")

    if shift > 0.5:
        verdict = "SUCCESSFUL RESOLUTION"
        detail = f"Sentiment improved by {shift:+.2f}"
    elif shift > 0:
        verdict = "SLIGHT IMPROVEMENT"
        detail = f"Sentiment improved by {shift:+.2f}"
    elif shift == 0:
        verdict = "NO CHANGE"
        detail = f"Sentiment stayed at {first:+.2f}"
    elif shift > -0.5:
        verdict = "SLIGHT DECLINE"
        detail = f"Sentiment dropped by {shift:+.2f}"
    else:
        verdict = "ESCALATION"
        detail = f"Sentiment dropped by {shift:+.2f}"

    print(f"  \u2502  Verdict: {verdict:<20} ({detail}){' ' * max(0, 19 - len(detail))}\u2502")
    print(f"  \u2514{'─' * 62}\u2518")

    # ASCII mini-chart
    print()
    _display_mini_chart(customer_turns)


def _display_mini_chart(customer_turns):
    """Display a compact ASCII chart of customer sentiment over time."""
    if len(customer_turns) < 2:
        return

    chart_rows = 11  # -1.0 to +1.0 in 0.2 increments
    y_labels = ["+1.0", "+0.8", "+0.6", "+0.4", "+0.2", " 0.0",
                "-0.2", "-0.4", "-0.6", "-0.8", "-1.0"]

    # Each customer turn gets a column
    col_spacing = max(6, min(12, 60 // len(customer_turns)))
    chart_width = col_spacing * len(customer_turns)

    for row in range(chart_rows):
        row_score = 1.0 - row * 0.2
        label = y_labels[row]
        line = f"  {label} \u2502"

        for ci, ct in enumerate(customer_turns):
            score = ct["score"]
            score_row = round((1.0 - score) / 0.2)
            score_row = max(0, min(10, score_row))

            col_start = ci * col_spacing
            cell = ""

            if score_row == row:
                marker = f" \u25cf"  # ● filled circle
                cell = marker + " " * (col_spacing - len(marker))
            elif row == 5:  # neutral line
                cell = "\u2500" * col_spacing  # ─
            else:
                cell = " " * col_spacing

            line += cell

        # Add right border for neutral line
        if row == 5:
            line += "\u2500"

        print(line)

    # X-axis
    x_axis = "       \u2514"
    for ci, ct in enumerate(customer_turns):
        x_axis += "\u2500" * col_spacing
    print(x_axis)

    # X-axis labels
    x_labels = "        "
    for ci, ct in enumerate(customer_turns):
        label = f"T{ct['turn']}"
        x_labels += label + " " * (col_spacing - len(label))
    print(x_labels)

    # Score labels below
    x_scores = "       "
    for ci, ct in enumerate(customer_turns):
        label = f"({ct['score']:+.1f})"
        x_scores += label + " " * (col_spacing - len(label))
    print(x_scores)


# ==============================================================================
# BONUS: Bulk analysis
# ==============================================================================

def bulk_analyze_all_conversations():
    """
    Analyze ALL unanalyzed conversations in the project.
    Useful when you have imported many conversations.
    """
    print("=" * 70)
    print("BULK ANALYSIS: Analyzing all conversations")
    print("=" * 70)

    client = contact_center_insights_v1.ContactCenterInsightsClient()

    request = contact_center_insights_v1.BulkAnalyzeConversationsRequest(
        parent=PARENT,
        filter="",  # Empty = all conversations
        analysis_percentage=100.0,  # Analyze 100%
    )

    print("  Starting bulk analysis (this can take a while)...")
    operation = client.bulk_analyze_conversations(request=request)

    result = operation.result(timeout=86400)
    print(f"  Bulk analysis complete!")
    print(f"    Successful: {result.successful_analysis_count}")
    print(f"    Failed: {result.failed_analysis_count}")
    return result


# ==============================================================================
# BONUS: List all conversations
# ==============================================================================

def list_conversations():
    """List all conversations in the project."""
    print("=" * 70)
    print("LIST: All conversations in this project")
    print("=" * 70)

    client = contact_center_insights_v1.ContactCenterInsightsClient()

    request = contact_center_insights_v1.ListConversationsRequest(
        parent=PARENT,
    )

    conversations = client.list_conversations(request=request)

    count = 0
    for convo in conversations:
        count += 1
        has_analysis = "Yes" if convo.latest_analysis else "No"
        print(f"  {count}. {convo.name}")
        print(f"     Medium: {convo.medium.name}, Analyzed: {has_analysis}")

    if count == 0:
        print("  No conversations found. Upload one first!")

    return count


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CCAI Insights: Turn-by-Turn Sentiment Analysis (Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python method3_python_client.py                    # Full pipeline, all features
  python method3_python_client.py --sentiment-only   # Only run sentiment annotator
  python method3_python_client.py --all-features     # Same as default
  python method3_python_client.py --bulk             # Bulk analyze all conversations
  python method3_python_client.py --list             # List all conversations
  python method3_python_client.py --analyze CONV_ID  # Analyze an existing conversation
        """,
    )
    parser.add_argument(
        "--sentiment-only",
        action="store_true",
        help="Only run the sentiment annotator (skip entity, intent, etc.)",
    )
    parser.add_argument(
        "--all-features",
        action="store_true",
        default=True,
        help="Display all analysis features (default: True)",
    )
    parser.add_argument(
        "--bulk",
        action="store_true",
        help="Bulk analyze all unanalyzed conversations",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all conversations in the project",
    )
    parser.add_argument(
        "--analyze",
        type=str,
        metavar="CONVERSATION_ID",
        help="Analyze an existing conversation by its ID (skip upload)",
    )
    parser.add_argument(
        "--skip-upload-to-gcs",
        action="store_true",
        default=True,
        help="Skip uploading to GCS (assumes file is already there)",
    )

    args = parser.parse_args()

    # ── Preflight checks ────────────────────────────────────────────────────
    if PROJECT_ID == "your-project-id":
        print("ERROR: Edit this script and set PROJECT_ID first.")
        print("       Open method3_python_client.py and change the CONFIGURATION section.")
        sys.exit(1)
    if BUCKET_NAME == "your-bucket-name":
        print("ERROR: Edit this script and set BUCKET_NAME first.")
        sys.exit(1)

    print()
    print("=" * 70)
    print("  CCAI Insights: Turn-by-Turn Sentiment Analysis")
    print("  Method 3 — Python Client Library")
    print("=" * 70)
    print(f"  Project:    {PROJECT_ID}")
    print(f"  Location:   {LOCATION}")
    print(f"  Bucket:     {BUCKET_NAME}")
    print(f"  Transcript: {GCS_TRANSCRIPT_URI}")
    print()

    # ── Mode: List conversations ────────────────────────────────────────────
    if args.list:
        list_conversations()
        return

    # ── Mode: Bulk analyze ──────────────────────────────────────────────────
    if args.bulk:
        bulk_analyze_all_conversations()
        return

    # ── Mode: Analyze existing conversation ─────────────────────────────────
    if args.analyze:
        conversation_name = f"{PARENT}/conversations/{args.analyze}"
        print(f"  Analyzing existing conversation: {conversation_name}")
        print()

        analysis_name = step3_analyze_conversation(
            conversation_name,
            sentiment_only=args.sentiment_only,
        )
        step4_display_results(conversation_name, show_all_features=True)
        return

    # ── Mode: Full pipeline (default) ───────────────────────────────────────
    # Step 1: Upload to GCS (optional, skip if already done)
    if not args.skip_upload_to_gcs:
        step1_upload_to_gcs()

    # Step 2: Upload conversation to CX Insights
    conversation_name = step2_upload_conversation(GCS_TRANSCRIPT_URI)

    # Step 3: Run analysis
    analysis_name = step3_analyze_conversation(
        conversation_name,
        sentiment_only=args.sentiment_only,
    )

    # Step 4: Display results
    step4_display_results(conversation_name, show_all_features=True)

    print()
    print("=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  Conversation: {conversation_name}")
    print(f"  Analysis:     {analysis_name}")
    print()
    print("  To re-view results later, run:")
    conversation_id = conversation_name.split("/")[-1]
    print(f"    python method3_python_client.py --analyze {conversation_id}")
    print()


if __name__ == "__main__":
    main()
