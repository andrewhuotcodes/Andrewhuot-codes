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

  2. Install dependencies:
       pip install -r requirements.txt
     Or:
       pip install google-cloud-contact-center-insights google-cloud-storage tabulate

  3. Authenticate:
       gcloud auth application-default login

  4. Edit the 3 variables in the CONFIGURATION section below.

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

    # ── 4a: Turn-by-Turn Sentiment ─────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  TURN-BY-TURN SENTIMENT ANALYSIS" + " " * 35 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_turn_sentiment(conversation)

    # ── 4b: Conversation-Level Sentiment ───────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  CONVERSATION-LEVEL SENTIMENT" + " " * 38 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_conversation_sentiment(conversation)

    if not show_all_features:
        return

    # ── 4c: Entity Extraction ──────────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ENTITY EXTRACTION" + " " * 49 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_entities(conversation)

    # ── 4d: Intent Detection ───────────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  INTENT DETECTION" + " " * 50 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_intents(conversation)

    # ── 4e: Issue/Topic Detection ──────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ISSUE / TOPIC DETECTION" + " " * 43 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_issues(conversation)

    # ── 4f: All Annotations Summary ────────────────────────────────────────
    print()
    print("+" + "-" * 68 + "+")
    print("|  ALL ANNOTATIONS SUMMARY" + " " * 43 + "|")
    print("+" + "-" * 68 + "+")
    print()

    _display_all_annotations(conversation)


def _display_turn_sentiment(conversation):
    """Display per-turn sentiment from annotations."""
    if not conversation.latest_analysis:
        print("  No analysis found. Run an analysis first.")
        return

    result = conversation.latest_analysis.analysis_result
    if not result or not result.call_analysis_metadata:
        print("  No call analysis metadata found.")
        return

    metadata = result.call_analysis_metadata
    annotations = metadata.annotations or []

    # Collect sentiment annotations
    sentiment_turns = []
    turn_num = 0
    for annotation in annotations:
        if annotation.sentiment_data:
            turn_num += 1
            channel = annotation.channel_tag
            role = "CUSTOMER" if channel == 1 else "AGENT"
            score = annotation.sentiment_data.score
            magnitude = annotation.sentiment_data.magnitude
            label = _get_sentiment_label(score, magnitude)

            sentiment_turns.append({
                "Turn": turn_num,
                "Speaker": role,
                "Score": f"{score:+.2f}",
                "Magnitude": f"{magnitude:.2f}",
                "Label": label,
            })

    if not sentiment_turns:
        print("  No sentiment annotations found.")
        print("  (This may happen if only agent turns are present,")
        print("   since CX Insights primarily scores customer turns.)")
        return

    if HAS_TABULATE:
        print(tabulate(sentiment_turns, headers="keys", tablefmt="rounded_grid"))
    else:
        # Fallback: simple formatted output
        print(f"  {'Turn':<6} {'Speaker':<10} {'Score':<8} {'Magnitude':<11} {'Label'}")
        print(f"  {'─' * 6} {'─' * 10} {'─' * 8} {'─' * 11} {'─' * 20}")
        for t in sentiment_turns:
            print(f"  {t['Turn']:<6} {t['Speaker']:<10} {t['Score']:<8} "
                  f"{t['Magnitude']:<11} {t['Label']}")


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
