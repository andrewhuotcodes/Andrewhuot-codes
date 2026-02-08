#!/usr/bin/env python3
"""
==============================================================================
Method 4: CX Insights DevKit — Audio Transcription + Analysis Pipeline
==============================================================================

WHAT THIS DOES:
  The CX Insights DevKit is a high-level Python library from Google that
  simplifies common workflows:
    - Transcribing audio files (mono/stereo) via Speech-to-Text
    - Recognizing speaker roles (who is the agent vs. customer)
    - Converting transcript formats (Genesys, AWS -> CX Insights format)
    - Uploading and ingesting conversations into CX Insights
    - Configuring BigQuery exports

  This script demonstrates two workflows:
    A) Processing an audio file (transcribe -> role recognition -> ingest)
    B) Ingesting an existing JSON transcript directly

WHEN TO USE THIS vs. METHOD 3:
  - Use Method 3 if you already have chat transcripts in CX Insights JSON format
  - Use Method 4 (this) if you need to:
    - Transcribe audio recordings first
    - Convert from other transcript formats (Genesys Cloud, AWS Connect)
    - Use automatic role recognition (who is agent vs. customer)
    - Perform bulk operations at scale

HOW TO RUN:
  1. Complete 00_setup.sh first

  2. Get the DevKit. Check the official documentation for the latest location:
     https://docs.google.com/contact-center/insights/docs/python-library-for-developers

     Typical setup:
       git clone <devkit-repository-url>
       cd ccai-insights-devkit
       pip install -r requirements.txt

  3. Authenticate:
       gcloud auth login
       gcloud auth application-default login
       gcloud config set project YOUR_PROJECT_ID

  4. Edit the CONFIGURATION section below.

  5. Run:
       python method4_devkit.py --workflow chat    # For chat transcripts
       python method4_devkit.py --workflow audio   # For audio files

==============================================================================

NOTE: The DevKit is a separate package from the core client library.
      If you don't have the DevKit installed, this script will show you
      what the code looks like and how to set it up.

==============================================================================
"""

import sys
import os
import json
import uuid
import argparse

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION — Edit these values                                        ║
# ╚════════════════════════════════════════════════════════════════════════════╝

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"

PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"

# For audio workflow: path to your audio file in GCS
AUDIO_GCS_PATH = f"gs://{BUCKET_NAME}/audio/call.wav"

# For audio workflow: Speech-to-Text recognizer resource name
# (Create one first via the Speech-to-Text console or API)
RECOGNIZER_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/default"

# For chat workflow: path to your transcript in GCS
CHAT_TRANSCRIPT_GCS_PATH = f"gs://{BUCKET_NAME}/transcripts/sample_conversation.json"


# ==============================================================================
# Check DevKit availability
# ==============================================================================

DEVKIT_AVAILABLE = False
try:
    # The DevKit package structure (as documented by Google)
    # Note: The actual import path may vary depending on the DevKit version.
    from ccai_insights_devkit import speech, format as fmt, storage, insights
    from ccai_insights_devkit import role_recognizer as rr
    DEVKIT_AVAILABLE = True
except ImportError:
    pass

# Also check if the standard client library is available (for fallback)
try:
    from google.cloud import contact_center_insights_v1
    STANDARD_CLIENT_AVAILABLE = True
except ImportError:
    STANDARD_CLIENT_AVAILABLE = False


# ==============================================================================
# WORKFLOW A: Audio file pipeline (Transcribe -> Role Recognition -> Ingest)
# ==============================================================================

def workflow_audio():
    """
    Full audio processing pipeline using the DevKit:
      1. Transcribe mono/stereo audio using Speech-to-Text V2
      2. Format the transcript
      3. Recognize speaker roles (agent vs. customer)
      4. Upload to Cloud Storage
      5. Ingest into CX Insights
    """
    print("=" * 70)
    print("WORKFLOW A: Audio File Pipeline")
    print("=" * 70)
    print()

    if not DEVKIT_AVAILABLE:
        print("The CX Insights DevKit is not installed.")
        print()
        print("Here's what the code would look like:")
        print()
        _print_audio_workflow_code()
        return

    # ── Step 1: Transcribe ──────────────────────────────────────────────────
    print("Step 1: Transcribing audio...")
    print(f"  Audio file: {AUDIO_GCS_PATH}")
    print(f"  Recognizer: {RECOGNIZER_PATH}")

    sp = speech.V2(project_id=PROJECT_ID)
    transcript = sp.create_transcription(
        audio_file_path=AUDIO_GCS_PATH,
        recognizer_path=RECOGNIZER_PATH,
    )
    print("  Transcription complete.")

    # ── Step 2: Format ──────────────────────────────────────────────────────
    print()
    print("Step 2: Formatting transcript to CX Insights format...")

    ft = fmt.Speech()
    transcript = ft.v2_recognizer_to_dict(transcript)
    print(f"  Formatted. {len(transcript.get('entries', []))} turns found.")

    # ── Step 3: Role Recognition ────────────────────────────────────────────
    print()
    print("Step 3: Recognizing speaker roles (agent vs. customer)...")

    role_recognizer = rr.RoleRecognizer()
    roles = role_recognizer.predict_roles(conversation=transcript)
    transcript = role_recognizer.combine(transcript, roles)
    print("  Roles assigned.")

    # ── Step 4: Upload to GCS ───────────────────────────────────────────────
    print()
    print("Step 4: Uploading formatted transcript to Cloud Storage...")

    gcs = storage.Gcs(project_name=PROJECT_ID, bucket_name=BUCKET_NAME)
    file_name = f"transcripts/devkit_{uuid.uuid4()}.json"
    gcs.upload_blob(file_name=file_name, data=transcript)
    gcs_path = f"gs://{BUCKET_NAME}/{file_name}"
    print(f"  Uploaded to: {gcs_path}")

    # ── Step 5: Ingest into CX Insights ─────────────────────────────────────
    print()
    print("Step 5: Ingesting into CX Insights...")

    ingestion = insights.Ingestion(
        parent=PARENT,
        transcript_path=gcs_path,
    )
    operation = ingestion.single()
    print("  Ingestion started (long-running operation).")
    print()
    print("  Next steps:")
    print("    1. Wait for the ingestion to complete")
    print("    2. Run analysis from the console or using Method 3")
    print("    3. View turn-by-turn sentiment results")

    return gcs_path


def _print_audio_workflow_code():
    """Print the audio workflow code for reference when DevKit is not installed."""
    code = '''
import uuid
from ccai_insights_devkit import speech, format as fmt, storage, insights
from ccai_insights_devkit import role_recognizer as rr

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"

# Step 1: Transcribe audio using Speech-to-Text V2
sp = speech.V2(project_id=PROJECT_ID)
transcript = sp.create_transcription(
    audio_file_path="gs://your-bucket/audio/call.wav",
    recognizer_path=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/default",
)

# Step 2: Format the transcript to CX Insights JSON format
ft = fmt.Speech()
transcript = ft.v2_recognizer_to_dict(transcript)

# Step 3: Recognize speaker roles (who is agent vs. customer)
role_recognizer = rr.RoleRecognizer()
roles = role_recognizer.predict_roles(conversation=transcript)
transcript = role_recognizer.combine(transcript, roles)

# Step 4: Upload formatted transcript to Cloud Storage
gcs = storage.Gcs(project_name=PROJECT_ID, bucket_name=BUCKET_NAME)
file_name = f"transcripts/devkit_{uuid.uuid4()}.json"
gcs.upload_blob(file_name=file_name, data=transcript)

# Step 5: Ingest into CX Insights
gcs_path = f"gs://{BUCKET_NAME}/{file_name}"
ingestion = insights.Ingestion(parent=PARENT, transcript_path=gcs_path)
operation = ingestion.single()

print("Conversation ingested! Run analysis from console or API.")
'''
    print(code)


# ==============================================================================
# WORKFLOW B: Chat transcript pipeline (direct ingest from GCS)
# ==============================================================================

def workflow_chat():
    """
    Chat transcript pipeline using the DevKit:
      1. Point to an existing JSON transcript in GCS
      2. Ingest into CX Insights
    """
    print("=" * 70)
    print("WORKFLOW B: Chat Transcript Pipeline")
    print("=" * 70)
    print()

    if not DEVKIT_AVAILABLE:
        print("The CX Insights DevKit is not installed.")
        print()
        if STANDARD_CLIENT_AVAILABLE:
            print("Falling back to the standard client library...")
            print()
            return _workflow_chat_standard_client()
        else:
            print("Here's what the code would look like:")
            print()
            _print_chat_workflow_code()
            return

    # ── Step 1: Ingest the transcript ────────────────────────────────────────
    print(f"Transcript path: {CHAT_TRANSCRIPT_GCS_PATH}")
    print()
    print("Ingesting into CX Insights...")

    ingestion = insights.Ingestion(
        parent=PARENT,
        transcript_path=CHAT_TRANSCRIPT_GCS_PATH,
    )
    operation = ingestion.single()

    print("Ingestion started (long-running operation).")
    print()
    print("Next steps:")
    print("  1. Wait for the ingestion to complete")
    print("  2. Open the CX Insights console to view and analyze")
    print("  3. Or use Method 3 to analyze via the Python client")

    return CHAT_TRANSCRIPT_GCS_PATH


def _workflow_chat_standard_client():
    """Fallback: use the standard client library instead of the DevKit."""
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    # Build the conversation object
    conversation = contact_center_insights_v1.Conversation()
    conversation.data_source.gcs_source.transcript_uri = CHAT_TRANSCRIPT_GCS_PATH
    conversation.medium = contact_center_insights_v1.Conversation.Medium.CHAT

    # Upload
    request = contact_center_insights_v1.UploadConversationRequest(
        parent=PARENT,
        conversation=conversation,
    )

    print(f"  Uploading {CHAT_TRANSCRIPT_GCS_PATH} to CX Insights...")
    operation = client.upload_conversation(request=request)

    print("  Waiting for upload...")
    result = operation.result(timeout=600)
    conversation_name = result.name
    print(f"  Conversation created: {conversation_name}")

    # Analyze
    print()
    print("  Running analysis with all annotators...")
    analysis = contact_center_insights_v1.Analysis()
    operation = client.create_analysis(
        parent=conversation_name,
        analysis=analysis,
    )

    result = operation.result(timeout=86400)
    print(f"  Analysis complete: {result.name}")

    # Retrieve results
    print()
    print("  Retrieving results...")
    conversation = client.get_conversation(name=conversation_name)

    if conversation.latest_analysis and conversation.latest_analysis.analysis_result:
        metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata

        if metadata.sentiments:
            print()
            print("  Conversation-Level Sentiment:")
            for s in metadata.sentiments:
                role = "Customer" if s.channel_tag == 1 else "Agent"
                print(f"    {role}: score={s.sentiment_data.score:+.2f}, "
                      f"magnitude={s.sentiment_data.magnitude:.2f}")

        if metadata.annotations:
            sentiment_annotations = [
                a for a in metadata.annotations if a.sentiment_data
            ]
            print()
            print(f"  Turn-by-Turn Sentiment ({len(sentiment_annotations)} annotated turns):")
            for i, a in enumerate(sentiment_annotations, 1):
                role = "CUSTOMER" if a.channel_tag == 1 else "AGENT"
                print(f"    Turn {i} ({role}): "
                      f"score={a.sentiment_data.score:+.2f}, "
                      f"magnitude={a.sentiment_data.magnitude:.2f}")

    return conversation_name


def _print_chat_workflow_code():
    """Print the chat workflow code for reference when DevKit is not installed."""
    code = '''
from ccai_insights_devkit import insights

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"

# Ingest a transcript that is already in GCS
ingestion = insights.Ingestion(
    parent=PARENT,
    transcript_path="gs://your-bucket/transcripts/sample_conversation.json",
)
operation = ingestion.single()

print("Conversation ingested! Run analysis from console or API.")
'''
    print(code)


# ==============================================================================
# WORKFLOW C: Format conversion (Genesys/AWS -> CX Insights)
# ==============================================================================

def show_format_conversion_examples():
    """
    Show how to convert transcripts from other platforms
    to the CX Insights format.
    """
    print("=" * 70)
    print("WORKFLOW C: Format Conversion Examples")
    print("=" * 70)
    print()
    print("The DevKit supports converting transcripts from:")
    print("  1. Genesys Cloud")
    print("  2. AWS Connect")
    print()
    print("These convert the platform-specific format to the CX Insights")
    print("JSON format (with entries[], role, user_id, etc.).")
    print()

    print("─" * 70)
    print("Example 1: Genesys Cloud -> CX Insights")
    print("─" * 70)
    print("""
from ccai_insights_devkit import format as fmt

# Convert a Genesys Cloud transcript
converter = fmt.GenesysCloud()
cx_insights_transcript = converter.to_insights_format(
    genesys_transcript=genesys_data  # Your Genesys transcript dict/JSON
)

# Result is in CX Insights JSON format, ready for ingestion
""")

    print("─" * 70)
    print("Example 2: AWS Connect -> CX Insights")
    print("─" * 70)
    print("""
from ccai_insights_devkit import format as fmt

# Convert an AWS Connect transcript
converter = fmt.AwsConnect()
cx_insights_transcript = converter.to_insights_format(
    aws_transcript=aws_data  # Your AWS Connect transcript dict/JSON
)

# Result is in CX Insights JSON format, ready for ingestion
""")

    print("─" * 70)
    print("Example 3: Custom format -> CX Insights")
    print("─" * 70)
    print("""
# If your transcript is in a custom format, convert it manually:
# The required CX Insights JSON format is:

{
  "entries": [
    {
      "text": "The message text",
      "role": "CUSTOMER",        # or "AGENT"
      "user_id": 1,              # 1 for customer, 2 for agent
      "start_timestamp_usec": 0  # Microseconds since epoch
    },
    ...
  ]
}

# Simply map your fields to this format and save as JSON.
""")


# ==============================================================================
# WORKFLOW D: BigQuery export configuration via DevKit
# ==============================================================================

def show_bigquery_setup():
    """Show how to configure BigQuery export using the DevKit."""
    print("=" * 70)
    print("WORKFLOW D: Configure BigQuery Export (DevKit)")
    print("=" * 70)
    print()
    print("The DevKit can configure BigQuery export for you:")
    print("""
from ccai_insights_devkit import insights

# Set up BigQuery export
settings = insights.Settings(parent=PARENT)
settings.set_bigquery_export(
    project_id="your-project-id",
    dataset="ccai_insights_data",
    table="conversations",
)

print("BigQuery export configured!")
print("Analyzed conversations will now be exported automatically.")
""")
    print()
    print("After configuring, any new analysis results will be automatically")
    print("exported to BigQuery. See Method 5 for SQL queries.")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CCAI Insights: DevKit Pipeline (Method 4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflows:
  --workflow audio      Process an audio file (transcribe -> analyze)
  --workflow chat       Ingest a chat transcript and analyze
  --workflow convert    Show format conversion examples
  --workflow bigquery   Show BigQuery export setup
  --workflow all        Show all workflow examples

Examples:
  python method4_devkit.py --workflow chat
  python method4_devkit.py --workflow audio
  python method4_devkit.py --workflow convert
  python method4_devkit.py --workflow all
        """,
    )
    parser.add_argument(
        "--workflow",
        type=str,
        choices=["audio", "chat", "convert", "bigquery", "all"],
        default="chat",
        help="Which workflow to run (default: chat)",
    )

    args = parser.parse_args()

    # ── Preflight ────────────────────────────────────────────────────────────
    if PROJECT_ID == "your-project-id":
        print("ERROR: Edit this script and set PROJECT_ID first.")
        sys.exit(1)

    print()
    print("=" * 70)
    print("  CCAI Insights: Turn-by-Turn Sentiment Analysis")
    print("  Method 4 — CX Insights DevKit")
    print("=" * 70)
    print(f"  Project:  {PROJECT_ID}")
    print(f"  Location: {LOCATION}")
    print(f"  Bucket:   {BUCKET_NAME}")
    print()

    if not DEVKIT_AVAILABLE:
        print("  NOTE: The CX Insights DevKit is not installed.")
        print("  The script will show you the code and fall back to")
        print("  the standard client library where possible.")
        print()
        print("  To install the DevKit, see:")
        print("  https://docs.google.com/contact-center/insights/docs/python-library-for-developers")
        print()

    # ── Run the selected workflow ────────────────────────────────────────────
    if args.workflow == "audio":
        workflow_audio()
    elif args.workflow == "chat":
        workflow_chat()
    elif args.workflow == "convert":
        show_format_conversion_examples()
    elif args.workflow == "bigquery":
        show_bigquery_setup()
    elif args.workflow == "all":
        workflow_chat()
        print("\n\n")
        workflow_audio()
        print("\n\n")
        show_format_conversion_examples()
        print("\n\n")
        show_bigquery_setup()

    print()
    print("=" * 70)
    print("  DONE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
