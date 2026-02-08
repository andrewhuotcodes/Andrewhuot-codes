# Turn-by-Turn Sentiment Analysis with Google Cloud CCAI Insights

## A Comprehensive Beginner's Guide

This guide walks you through performing **turn-by-turn sentiment analysis** on contact center conversations using **Google Cloud Customer Experience Insights** (formerly CCAI Insights / Conversational Insights). You will learn multiple ways to achieve this — from the Google Cloud Console UI, to the REST API with `curl`, to the Python client library.

---

## Table of Contents

1. [What is CCAI Insights?](#1-what-is-ccai-insights)
2. [How Sentiment Analysis Works](#2-how-sentiment-analysis-works)
3. [Prerequisites & Initial Setup](#3-prerequisites--initial-setup)
4. [Prepare Your Conversation Data](#4-prepare-your-conversation-data)
5. [Method 1: Google Cloud Console (No Code)](#5-method-1-google-cloud-console-no-code)
6. [Method 2: REST API with curl](#6-method-2-rest-api-with-curl)
7. [Method 3: Python Client Library](#7-method-3-python-client-library)
8. [Method 4: Python DevKit (High-Level)](#8-method-4-python-devkit-high-level)
9. [Understanding the Analysis Results](#9-understanding-the-analysis-results)
10. [Method 5: Export to BigQuery for SQL Analysis](#10-method-5-export-to-bigquery-for-sql-analysis)
11. [All CCAI Insights Features Overview](#11-all-ccai-insights-features-overview)
12. [Pricing](#12-pricing)
13. [Troubleshooting](#13-troubleshooting)
14. [Resources & Links](#14-resources--links)

---

## 1. What is CCAI Insights?

**Customer Experience Insights** (CX Insights) is a Google Cloud product that uses machine learning to analyze contact center conversations. You feed it transcripts or audio recordings, and it returns rich analytics including:

- **Sentiment analysis** (turn-by-turn and conversation-level)
- **Topic/issue detection** (what the call is about)
- **Entity extraction** (products, dates, locations mentioned)
- **Intent detection** (what the customer is trying to do)
- **Silence detection** (dead air in calls)
- **Interruption detection** (people talking over each other)
- **Conversation summaries**
- **Phrase matching** (custom keyword/phrase detection)
- **Quality AI** (agent scorecards and evaluations)

The product sits at: [https://cloud.google.com/solutions/ccai-insights](https://cloud.google.com/solutions/ccai-insights)

---

## 2. How Sentiment Analysis Works

### What Gets Measured

CX Insights measures the **emotional intent** of messages in a conversation. It focuses on **end-user (customer) sentiment** in contact center conversations, though agent sentiment is also captured at the conversation level.

### Turn-Level (Per-Message) Sentiment Scores

Each individual customer turn in the conversation gets a sentiment score. The system uses **eight granular categories**:

| Score | Magnitude | Label | Classification |
|-------|-----------|------|----------------|
| -1.0 | 1.0 | `negative` | Negative |
| -0.5 | 0.5 | `somewhat_negative` | Negative |
| -0.25 | 0.75 | `mixed_more_negative` | Negative |
| 0.0 | 0.0 | `neutral` | Neutral |
| 0.0 | 0.75 | `mixed_balanced` | Neutral |
| 0.25 | 0.75 | `mixed_more_positive` | Positive |
| 0.5 | 0.5 | `somewhat_positive` | Positive |
| 1.0 | 1.0 | `positive` | Positive |

### Conversation-Level Sentiment

The overall conversation also gets a sentiment classification using broader thresholds:

- **Positive**: score >= 0.5
- **Neutral**: score between -0.5 and 0.5
- **Negative**: score <= -0.5

### Score vs. Magnitude

- **Score** (-1.0 to 1.0): How positive or negative the statement is
- **Magnitude** (0.0 to infinity): The *strength* of the emotion, regardless of whether it is positive or negative. A score of 0.0 with a high magnitude indicates mixed sentiment; a score of 0.0 with low magnitude indicates neutral sentiment.

---

## 3. Prerequisites & Initial Setup

### Step 3.1: Create a Google Cloud Project

If you don't already have one:

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown at the top, then **New Project**
3. Name your project (e.g., `ccai-insights-demo`)
4. Click **Create**
5. Note your **Project ID** — you will need it throughout this guide

### Step 3.2: Enable Billing

CCAI Insights requires a billing account. Go to **Billing** in the Cloud Console and link a billing account to your project.

### Step 3.3: Enable Required APIs

You must enable several APIs. The easiest way is via Cloud Shell or your local terminal with the `gcloud` CLI installed.

**Option A: Using Cloud Shell (in your browser)**

Open Cloud Shell from the top-right of the Cloud Console (the `>_` icon), then run:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable all required APIs in one command
gcloud services enable \
  contactcenterinsights.googleapis.com \
  speech.googleapis.com \
  storage.googleapis.com \
  dlp.googleapis.com \
  language.googleapis.com
```

**Option B: Using the Console UI**

1. Go to **APIs & Services > Library**
2. Search for and enable each of these:
   - **Contact Center AI Insights API** (or "Customer Experience Insights API")
   - **Cloud Speech-to-Text API**
   - **Cloud Storage API**
   - **Cloud Data Loss Prevention (DLP) API**
   - **Cloud Natural Language API**

### Step 3.4: Set Up Authentication

**For local development:**

```bash
# Install the Google Cloud CLI if you haven't:
# https://cloud.google.com/sdk/docs/install

# Log in
gcloud auth login

# Set Application Default Credentials (ADC)
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

**For service accounts (production use):**

```bash
# Create a service account
gcloud iam service-accounts create ccai-insights-sa \
  --display-name="CCAI Insights Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:ccai-insights-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/contactcenterinsights.editor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:ccai-insights-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:ccai-insights-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/speech.admin"

# Create and download a key file
gcloud iam service-accounts keys create key.json \
  --iam-account=ccai-insights-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/key.json"
```

### Step 3.5: Create a Cloud Storage Bucket

You need a GCS bucket to store your conversation data (transcripts and/or audio):

```bash
# Create a bucket (choose a region close to you)
gcloud storage buckets create gs://YOUR_BUCKET_NAME \
  --location=us-central1 \
  --default-storage-class=STANDARD
```

---

## 4. Prepare Your Conversation Data

CX Insights accepts two types of input: **chat transcripts** (JSON) and **voice recordings** (audio files with optional transcripts).

### Chat Transcript Format (JSON)

This is the easiest way to get started. Create a JSON file that represents a conversation. Each message is an "entry" with a role, text, timestamp, and user ID.

**Create this file and save it as `sample_conversation.json`:**

```json
{
  "entries": [
    {
      "text": "Hi, I've been having problems with my internet connection for the past three days. It keeps dropping every few hours and it's really frustrating.",
      "role": "CUSTOMER",
      "user_id": 1,
      "start_timestamp_usec": 1000000
    },
    {
      "text": "I'm sorry to hear that you're experiencing connectivity issues. I'd be happy to help you troubleshoot this. Can you tell me what type of internet plan you're on?",
      "role": "AGENT",
      "user_id": 2,
      "start_timestamp_usec": 5000000
    },
    {
      "text": "I'm on the Premium 500 Mbps plan. I'm paying $89 a month for this and the service has been terrible lately. I'm seriously considering switching providers.",
      "role": "CUSTOMER",
      "user_id": 1,
      "start_timestamp_usec": 12000000
    },
    {
      "text": "I completely understand your frustration, and I want to make sure we resolve this for you today. Let me check the network status in your area. Can I have your account number or the phone number associated with your account?",
      "role": "AGENT",
      "user_id": 2,
      "start_timestamp_usec": 20000000
    },
    {
      "text": "Sure, my account number is 7829456. I just want this fixed. I work from home and the constant disconnections are affecting my job.",
      "role": "CUSTOMER",
      "user_id": 1,
      "start_timestamp_usec": 28000000
    },
    {
      "text": "Thank you. I can see there was a network maintenance event in your area that ended yesterday, but I'm also noticing some signal issues on your line. I'd like to schedule a technician visit to check your connection. Would tomorrow between 9 AM and 12 PM work for you?",
      "role": "AGENT",
      "user_id": 2,
      "start_timestamp_usec": 35000000
    },
    {
      "text": "Tomorrow morning works. But what about the three days I've already lost? I think I should get a credit for the downtime.",
      "role": "CUSTOMER",
      "user_id": 1,
      "start_timestamp_usec": 45000000
    },
    {
      "text": "Absolutely, that's a fair request. I've gone ahead and applied a 5-day service credit to your account, which comes to $14.83. You'll see that reflected on your next bill. Is there anything else I can help you with today?",
      "role": "AGENT",
      "user_id": 2,
      "start_timestamp_usec": 52000000
    },
    {
      "text": "No, that covers it. I appreciate you taking care of the credit without me having to argue about it. Thank you for your help.",
      "role": "CUSTOMER",
      "user_id": 1,
      "start_timestamp_usec": 60000000
    },
    {
      "text": "You're welcome! I've booked the technician for tomorrow between 9 and 12. You'll receive a confirmation text shortly. If you experience any issues before then, don't hesitate to call back. Have a great day!",
      "role": "AGENT",
      "user_id": 2,
      "start_timestamp_usec": 65000000
    }
  ]
}
```

#### JSON Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `entries` | Yes | Array of messages in chronological order |
| `entries[].text` | Yes | The message content |
| `entries[].role` | Yes | `CUSTOMER`, `AGENT`, `AUTOMATED_AGENT`, or `END_USER` |
| `entries[].user_id` | Yes | Numeric ID for the participant (consistent within a conversation) |
| `entries[].start_timestamp_usec` | Yes | Timestamp in microseconds since Unix epoch (UTC) |
| `conversation_info` | No | Optional metadata object |
| `conversation_info.categories` | No | Array of `{ "display_name": "..." }` objects for custom categories |

### Upload the Transcript to Cloud Storage

```bash
# Upload your JSON transcript to the bucket
gcloud storage cp sample_conversation.json gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json
```

Verify it was uploaded:

```bash
gcloud storage ls gs://YOUR_BUCKET_NAME/transcripts/
```

---

## 5. Method 1: Google Cloud Console (No Code)

This is the simplest way to get started — everything is done through the browser.

### Step 5.1: Open CX Insights Console

Navigate to: [https://ccai.cloud.google.com/insights/projects](https://ccai.cloud.google.com/insights/projects)

Or from the Cloud Console:
1. Go to the Navigation Menu (hamburger icon, top-left)
2. Search for **"Contact Center AI Insights"** or **"Customer Experience Insights"**
3. Click on it

Enter your Project ID if prompted.

### Step 5.2: Import a Conversation

1. Click **Conversation Hub** in the left sidebar
2. Click the **Import** button
3. Select the conversation type:
   - Choose **Chat** (for our JSON transcript example)
   - Or choose **Voice** (if you have audio recordings)
4. Click **Next**

#### For Chat Import:
1. Select **File** (for a single conversation)
2. In the **Transcript URI** field, enter your GCS path:
   ```
   gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json
   ```
3. Click **Next**
4. Enter an **Agent ID** (any identifier for the agent, e.g., `agent-001`)
5. Click **Import**

#### For Voice Import:
1. Select **File**
2. Enter the audio file path in **Audio URI** (e.g., `gs://YOUR_BUCKET_NAME/audio/call.wav`)
3. Optionally check **Provide a transcript** and enter the transcript URI
4. Click **Next**
5. Enter an **Agent ID**
6. Select the agent's **audio track** (1 or 2)
7. Click **Import**

> **Note:** Audio files must have exactly **two channels**. Other channel counts will cause an error during analysis.

### Step 5.3: Analyze the Conversation

1. After import completes, you will see your conversation listed in the Conversation Hub
2. Click on the **conversation name** to open it
3. Click the **Analyze** button
4. Wait for the analysis to complete (this may take a minute or two)

### Step 5.4: View Turn-by-Turn Sentiment Results

Once analysis completes:

1. Navigate to the **Conversation spotlight** section on the conversation details page
2. You will see:
   - **Sentiment timeline**: A visual chart showing sentiment changes across the conversation
   - **Positive moments** highlighted in **blue**
   - **Negative moments** highlighted in **red**
   - Each turn of the conversation annotated with its sentiment score
3. The **Information** tab shows detailed rationale for sentiment scores

You can also view agent-level sentiment:
1. Go to **Quality AI > Conversations** in the left sidebar
2. Select a conversation
3. Review the **Conversation spotlight** section
4. View per-agent sentiment scores and averages

---

## 6. Method 2: REST API with curl

This approach gives you full programmatic control using simple HTTP requests.

### Step 6.1: Upload a Conversation via the API

First, upload your conversation transcript to the Insights service:

```bash
# Set your variables
PROJECT_ID="your-project-id"
LOCATION="us-central1"
BUCKET_NAME="your-bucket-name"

# Create the request body
cat > upload_request.json << 'EOF'
{
  "conversation": {
    "dataSource": {
      "gcsSource": {
        "transcriptUri": "gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json"
      }
    },
    "medium": "CHAT",
    "qualityMetadata": {
      "agentInfo": [
        {
          "agentId": "agent-001",
          "displayName": "Support Agent"
        }
      ]
    }
  }
}
EOF

# Replace the bucket name placeholder in the file
sed -i "s/YOUR_BUCKET_NAME/$BUCKET_NAME/g" upload_request.json

# Upload the conversation
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @upload_request.json \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations:upload"
```

**Expected response** — a long-running operation:

```json
{
  "name": "projects/YOUR_PROJECT_ID/locations/us-central1/operations/OPERATION_ID"
}
```

### Step 6.2: Poll the Upload Operation

The upload is asynchronous. Poll until it completes:

```bash
OPERATION_ID="your-operation-id-from-previous-step"

curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/operations/$OPERATION_ID"
```

When the `done` field is `true`, the response will include the conversation resource name. Extract the `CONVERSATION_ID` from the response (it will be in the `name` field of the result).

### Step 6.3: Create an Analysis (with Sentiment Enabled)

Now analyze the conversation. You can run all annotators or select specific ones:

**Run ALL annotators (default):**

```bash
CONVERSATION_ID="your-conversation-id"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{}' \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID/analyses"
```

**Run ONLY the sentiment annotator:**

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "annotatorSelector": {
      "runSentimentAnnotator": true
    }
  }' \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID/analyses"
```

**Run multiple specific annotators:**

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "annotatorSelector": {
      "runSentimentAnnotator": true,
      "runEntityAnnotator": true,
      "runIntentAnnotator": true,
      "runSilenceAnnotator": true,
      "runInterruptionAnnotator": true,
      "runIssueModelAnnotator": true
    }
  }' \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID/analyses"
```

### Available Annotators Reference

| Annotator | JSON Field | What It Does |
|-----------|-----------|--------------|
| Sentiment | `runSentimentAnnotator` | Per-turn and conversation-level sentiment scores |
| Entity | `runEntityAnnotator` | Extracts entities (names, products, dates, etc.) |
| Intent | `runIntentAnnotator` | Detects the customer's intent |
| Silence | `runSilenceAnnotator` | Detects periods of silence |
| Interruption | `runInterruptionAnnotator` | Detects when speakers talk over each other |
| Issue Model | `runIssueModelAnnotator` | Classifies the conversation topic/issue |
| Phrase Matcher | `runPhraseMatcherAnnotator` | Matches custom phrases you have defined |

### Step 6.4: Poll the Analysis Operation

```bash
ANALYSIS_OPERATION_ID="operation-id-from-previous-step"

curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/operations/$ANALYSIS_OPERATION_ID"
```

### Step 6.5: Retrieve the Analysis Results

Once the operation completes, list the analyses for the conversation:

```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID/analyses"
```

Or get a specific analysis:

```bash
ANALYSIS_ID="your-analysis-id"

curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID/analyses/$ANALYSIS_ID"
```

### Step 6.6: Get the Full Conversation with Annotations

To see the complete conversation with all annotations (including per-turn sentiment), retrieve the conversation resource:

```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations/$CONVERSATION_ID"
```

---

## 7. Method 3: Python Client Library

This method uses the official Google Cloud Python client library for a more structured, programmatic approach.

### Step 7.1: Install the Library

```bash
# Create a virtual environment (recommended)
python3 -m venv ccai-env
source ccai-env/bin/activate

# Install the client library
pip install google-cloud-contact-center-insights

# Also install the storage library for uploading files
pip install google-cloud-storage
```

### Step 7.2: Complete Python Script

Save the following as `ccai_sentiment_analysis.py`:

```python
"""
CCAI Insights: Turn-by-Turn Sentiment Analysis
Complete example using the Python client library.
"""

import json
import time
from google.cloud import contact_center_insights_v1
from google.cloud import storage


# ============================================================
# CONFIGURATION — Update these values for your environment
# ============================================================
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"
TRANSCRIPT_FILENAME = "sample_conversation.json"

# Derived values
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
GCS_TRANSCRIPT_URI = f"gs://{BUCKET_NAME}/transcripts/{TRANSCRIPT_FILENAME}"


def upload_transcript_to_gcs(local_file_path: str) -> str:
    """Upload a local JSON transcript file to Google Cloud Storage."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"transcripts/{TRANSCRIPT_FILENAME}")
    blob.upload_from_filename(local_file_path)
    gcs_uri = f"gs://{BUCKET_NAME}/transcripts/{TRANSCRIPT_FILENAME}"
    print(f"Uploaded transcript to {gcs_uri}")
    return gcs_uri


def upload_conversation(gcs_transcript_uri: str) -> str:
    """
    Upload a conversation to CX Insights and return
    the conversation resource name.
    """
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

    # Upload returns a long-running operation
    print("Uploading conversation...")
    operation = client.upload_conversation(request=request)

    # Wait for the operation to complete
    print("Waiting for upload to complete...")
    result = operation.result(timeout=600)  # 10 minute timeout
    print(f"Conversation uploaded: {result.name}")
    return result.name


def create_conversation_directly() -> str:
    """
    Alternative: Create a conversation directly by building
    the transcript inline (without uploading to GCS first).
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    conversation = contact_center_insights_v1.Conversation()
    conversation.data_source.gcs_source.transcript_uri = GCS_TRANSCRIPT_URI
    conversation.medium = contact_center_insights_v1.Conversation.Medium.CHAT

    request = contact_center_insights_v1.CreateConversationRequest(
        parent=PARENT,
        conversation=conversation,
    )

    result = client.create_conversation(request=request)
    print(f"Conversation created: {result.name}")
    return result.name


def analyze_conversation(conversation_name: str) -> str:
    """
    Run analysis on a conversation with all annotators enabled.
    Returns the analysis resource name.
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    # Create an analysis with the sentiment annotator enabled
    analysis = contact_center_insights_v1.Analysis()

    # Optionally configure specific annotators:
    # analysis.annotator_selector.run_sentiment_annotator = True
    # analysis.annotator_selector.run_entity_annotator = True
    # analysis.annotator_selector.run_intent_annotator = True
    # analysis.annotator_selector.run_silence_annotator = True
    # analysis.annotator_selector.run_interruption_annotator = True
    # analysis.annotator_selector.run_issue_model_annotator = True

    # If you leave the annotator_selector empty, ALL annotators run by default.

    print("Starting analysis (this may take a minute)...")
    operation = client.create_analysis(
        parent=conversation_name,
        analysis=analysis,
    )

    # Wait for the long-running operation to complete
    result = operation.result(timeout=86400)  # 24 hour timeout (generous)
    print(f"Analysis complete: {result.name}")
    return result.name


def analyze_with_specific_annotators(conversation_name: str) -> str:
    """
    Run analysis with only specific annotators.
    Useful if you only need sentiment and entities, for example.
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    analysis = contact_center_insights_v1.Analysis()

    # Enable only the annotators you need
    analysis.annotator_selector.run_sentiment_annotator = True
    analysis.annotator_selector.run_entity_annotator = True
    analysis.annotator_selector.run_intent_annotator = True

    print("Starting targeted analysis...")
    operation = client.create_analysis(
        parent=conversation_name,
        analysis=analysis,
    )

    result = operation.result(timeout=86400)
    print(f"Analysis complete: {result.name}")
    return result.name


def get_analysis_results(analysis_name: str):
    """Retrieve and display the full analysis results."""
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    analysis = client.get_analysis(name=analysis_name)
    return analysis


def get_conversation_with_annotations(conversation_name: str):
    """Retrieve the full conversation resource with annotations."""
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    conversation = client.get_conversation(name=conversation_name)
    return conversation


def display_turn_by_turn_sentiment(conversation_name: str):
    """
    Retrieve a conversation and display turn-by-turn sentiment
    in a readable format.
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()
    conversation = client.get_conversation(name=conversation_name)

    print("\n" + "=" * 70)
    print("TURN-BY-TURN SENTIMENT ANALYSIS")
    print("=" * 70)

    # Display the transcript with sentiment per turn
    if conversation.transcript and conversation.transcript.transcript_segments:
        for i, segment in enumerate(conversation.transcript.transcript_segments):
            role = "UNKNOWN"
            if segment.channel_tag == 1:
                role = "CUSTOMER"
            elif segment.channel_tag == 2:
                role = "AGENT"

            # Get the text of this segment
            text = segment.segment_participant.role if hasattr(segment, 'segment_participant') else ""
            words = " ".join([w.word for w in segment.words]) if segment.words else ""

            # Get sentiment for this segment
            sentiment_score = segment.sentiment.score if segment.sentiment else "N/A"
            sentiment_magnitude = segment.sentiment.magnitude if segment.sentiment else "N/A"

            print(f"\n--- Turn {i + 1} ({role}) ---")
            if words:
                print(f"Text: {words}")
            if sentiment_score != "N/A":
                label = get_sentiment_label(sentiment_score, sentiment_magnitude)
                print(f"Sentiment Score: {sentiment_score}")
                print(f"Sentiment Magnitude: {sentiment_magnitude}")
                print(f"Sentiment Label: {label}")

    # Also display analysis annotations if available
    if conversation.latest_analysis and conversation.latest_analysis.analysis_result:
        result = conversation.latest_analysis.analysis_result
        if result.call_analysis_metadata:
            metadata = result.call_analysis_metadata

            # Display per-turn annotations
            if metadata.annotations:
                print("\n" + "=" * 70)
                print("DETAILED ANNOTATIONS")
                print("=" * 70)
                for annotation in metadata.annotations:
                    if annotation.sentiment_data:
                        print(f"\n  Channel: {annotation.channel_tag}")
                        print(f"  Score: {annotation.sentiment_data.score}")
                        print(f"  Magnitude: {annotation.sentiment_data.magnitude}")
                        label = get_sentiment_label(
                            annotation.sentiment_data.score,
                            annotation.sentiment_data.magnitude
                        )
                        print(f"  Label: {label}")

            # Display conversation-level sentiment
            if metadata.sentiments:
                print("\n" + "=" * 70)
                print("CONVERSATION-LEVEL SENTIMENT")
                print("=" * 70)
                for sentiment in metadata.sentiments:
                    channel_label = "Customer" if sentiment.channel_tag == 1 else "Agent"
                    print(f"\n  {channel_label} (Channel {sentiment.channel_tag}):")
                    print(f"    Score: {sentiment.sentiment_data.score}")
                    print(f"    Magnitude: {sentiment.sentiment_data.magnitude}")


def get_sentiment_label(score: float, magnitude: float) -> str:
    """Convert a score and magnitude to a human-readable sentiment label."""
    if score is None or score == "N/A":
        return "N/A"

    score = float(score)
    magnitude = float(magnitude) if magnitude and magnitude != "N/A" else 0

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


def display_all_features(conversation_name: str):
    """
    Display ALL analysis features — not just sentiment.
    Shows the full power of CCAI Insights.
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()
    conversation = client.get_conversation(name=conversation_name)

    if not conversation.latest_analysis or not conversation.latest_analysis.analysis_result:
        print("No analysis results found. Run an analysis first.")
        return

    result = conversation.latest_analysis.analysis_result
    metadata = result.call_analysis_metadata

    # 1. SENTIMENT
    print("\n" + "=" * 70)
    print("1. SENTIMENT ANALYSIS")
    print("=" * 70)
    if metadata.sentiments:
        for s in metadata.sentiments:
            label = "Customer" if s.channel_tag == 1 else "Agent"
            print(f"  {label}: score={s.sentiment_data.score}, "
                  f"magnitude={s.sentiment_data.magnitude}")

    # 2. ENTITIES
    print("\n" + "=" * 70)
    print("2. ENTITY EXTRACTION")
    print("=" * 70)
    if metadata.entities:
        for name, entity_data in metadata.entities.items():
            print(f"  Entity: {name}")
            print(f"    Type: {entity_data.type_}")
            if entity_data.sentiment:
                print(f"    Sentiment: {entity_data.sentiment.score}")

    # 3. INTENTS
    print("\n" + "=" * 70)
    print("3. INTENT DETECTION")
    print("=" * 70)
    if metadata.intents:
        for name, intent_data in metadata.intents.items():
            print(f"  Intent: {name} (ID: {intent_data.id})")

    # 4. ISSUES
    print("\n" + "=" * 70)
    print("4. ISSUE/TOPIC DETECTION")
    print("=" * 70)
    if metadata.issue_model_result:
        for issue in metadata.issue_model_result.issues:
            print(f"  Issue: {issue.issue}")
            print(f"    Score: {issue.score}")

    # 5. ALL ANNOTATIONS (including silence, interruptions, etc.)
    print("\n" + "=" * 70)
    print("5. ALL ANNOTATIONS")
    print("=" * 70)
    if metadata.annotations:
        for i, annotation in enumerate(metadata.annotations):
            print(f"\n  Annotation {i + 1}:")
            if annotation.sentiment_data:
                print(f"    Type: Sentiment")
                print(f"    Score: {annotation.sentiment_data.score}")
                print(f"    Magnitude: {annotation.sentiment_data.magnitude}")
            elif annotation.silence_data:
                print(f"    Type: Silence")
            elif annotation.interruption_data:
                print(f"    Type: Interruption")
            elif annotation.entity_mention_data:
                print(f"    Type: Entity Mention")
                print(f"    Text: {annotation.entity_mention_data.entity_unique_id}")
            elif annotation.intent_match_data:
                print(f"    Type: Intent Match")
                print(f"    Intent: {annotation.intent_match_data.intent_unique_id}")
            print(f"    Channel: {annotation.channel_tag}")


def bulk_analyze_conversations(filter_query: str = ""):
    """
    Bulk analyze multiple conversations at once.
    Useful for processing large batches.
    """
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    request = contact_center_insights_v1.BulkAnalyzeConversationsRequest(
        parent=PARENT,
        filter=filter_query,  # e.g., "" for all, or a filter expression
        analysis_percentage=100.0,  # Analyze 100% of matching conversations
    )

    print("Starting bulk analysis...")
    operation = client.bulk_analyze_conversations(request=request)

    # This can take a long time for many conversations
    result = operation.result(timeout=86400)
    print(f"Bulk analysis complete. "
          f"Successful: {result.successful_analysis_count}, "
          f"Failed: {result.failed_analysis_count}")
    return result


# ============================================================
# MAIN — Run the full pipeline
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("CCAI Insights: Turn-by-Turn Sentiment Analysis")
    print("=" * 70)

    # Step 1: Upload transcript to GCS (skip if already uploaded)
    # upload_transcript_to_gcs("sample_conversation.json")

    # Step 2: Upload conversation to CX Insights
    conversation_name = upload_conversation(GCS_TRANSCRIPT_URI)

    # Step 3: Run analysis with all annotators
    analysis_name = analyze_conversation(conversation_name)

    # Step 4: Display turn-by-turn sentiment
    display_turn_by_turn_sentiment(conversation_name)

    # Step 5: Display all features
    display_all_features(conversation_name)

    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)
```

### Step 7.3: Run the Script

```bash
# Make sure you are authenticated
gcloud auth application-default login

# Run the script
python ccai_sentiment_analysis.py
```

---

## 8. Method 4: Python DevKit (High-Level)

Google provides a higher-level **CX Insights DevKit** that simplifies common workflows like transcription, role recognition, and ingestion.

### Step 8.1: Install the DevKit

```bash
# Clone or download the devkit
# (Check the official docs for the latest location)
# https://docs.cloud.google.com/contact-center/insights/docs/python-library-for-developers

# Install dependencies
pip install -r requirements.txt
```

### Step 8.2: Authenticate

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Step 8.3: Example — Audio with Role Recognition and Analysis

The DevKit provides a streamlined workflow for processing audio files:

```python
import uuid
from ccai_insights_devkit import speech, format, storage, insights, rr

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"

# Step 1: Transcribe audio using Speech-to-Text V2
sp = speech.V2(project_id=PROJECT_ID)
transcript = sp.create_transcription(
    audio_file_path="gs://your-bucket/audio/call.wav",
    recognizer_path=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/your-recognizer"
)

# Step 2: Format the transcript
ft = format.Speech()
transcript = ft.v2_recognizer_to_dict(transcript)

# Step 3: Recognize speaker roles using Gemini
role_recognizer = rr.RoleRecognizer()
roles = role_recognizer.predict_roles(conversation=transcript)
transcript = role_recognizer.combine(transcript, roles)

# Step 4: Upload to Cloud Storage
gcs = storage.Gcs(project_name=PROJECT_ID, bucket_name=BUCKET_NAME)
file_name = f"{uuid.uuid4()}.json"
gcs.upload_blob(file_name=file_name, data=transcript)

# Step 5: Ingest into CX Insights
gcs_path = f"gs://{BUCKET_NAME}/{file_name}"
ingestion = insights.Ingestion(parent=PARENT, transcript_path=gcs_path)
operation = ingestion.single()

# The conversation is now in CX Insights and can be analyzed
print(f"Conversation ingested. Run analysis from the console or API.")
```

> **Note:** The DevKit is ideal for workflows involving audio transcription and format conversion (e.g., from Genesys Cloud or AWS formats). For simple chat transcript analysis, Methods 2 or 3 are more straightforward.

---

## 9. Understanding the Analysis Results

### Analysis Result Structure

When you retrieve an analysis, the results are organized as follows:

```
Analysis
└── analysisResult
    └── callAnalysisMetadata
        ├── annotations[]              ← Per-turn annotations
        │   ├── sentimentData          ← Turn-level sentiment
        │   │   ├── score              ← -1.0 to 1.0
        │   │   └── magnitude          ← 0.0 to infinity
        │   ├── silenceData            ← Silence annotations
        │   ├── interruptionData       ← Interruption annotations
        │   ├── entityMentionData      ← Entity mentions
        │   ├── intentMatchData        ← Intent matches
        │   ├── channelTag             ← Speaker (1=customer, 2=agent)
        │   ├── annotationStartBoundary
        │   └── annotationEndBoundary
        ├── sentiments[]               ← Conversation-level sentiment
        │   ├── channelTag
        │   └── sentimentData
        │       ├── score
        │       └── magnitude
        ├── entities{}                 ← Extracted entities
        ├── intents{}                  ← Detected intents
        └── issueModelResult           ← Topic classification
```

### Example: Interpreting Turn-by-Turn Sentiment

For our sample conversation, the analysis would produce annotations like:

| Turn | Speaker | Text (abbreviated) | Score | Magnitude | Label |
|------|---------|-------------------|-------|-----------|-------|
| 1 | Customer | "problems with internet...really frustrating" | -0.5 | 0.5 | Somewhat Negative |
| 2 | Agent | "sorry to hear...happy to help" | — | — | (Agent, not scored) |
| 3 | Customer | "terrible service...considering switching" | -1.0 | 1.0 | Negative |
| 4 | Agent | "understand your frustration...resolve this" | — | — | (Agent, not scored) |
| 5 | Customer | "affecting my job" | -0.5 | 0.5 | Somewhat Negative |
| 6 | Agent | "schedule a technician" | — | — | (Agent, not scored) |
| 7 | Customer | "should get a credit" | -0.25 | 0.75 | Mixed (More Negative) |
| 8 | Agent | "applied a 5-day credit" | — | — | (Agent, not scored) |
| 9 | Customer | "appreciate you...thank you" | 1.0 | 1.0 | Positive |
| 10 | Agent | "You're welcome!" | — | — | (Agent, not scored) |

> **Key insight:** Notice how sentiment shifts from negative to positive as the agent resolves the issue. This is exactly what turn-by-turn sentiment analysis reveals — the *emotional journey* of the conversation.

---

## 10. Method 5: Export to BigQuery for SQL Analysis

For large-scale analysis across many conversations, export your data to BigQuery and query it with SQL.

### Step 10.1: Set Up BigQuery Export

**Via the Console:**

1. In the CX Insights console, go to **Settings**
2. Find the **BigQuery export** section
3. Configure your BigQuery dataset and table
4. Enable the export

**Via the API:**

```bash
curl -X PATCH \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "pubsubNotificationSettings": {},
    "analysisConfig": {
      "runtimeIntegrationAnalysisPercentage": 100
    }
  }' \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/settings"
```

### Step 10.2: Export Conversations

```bash
# Create a BigQuery dataset first
bq mk --dataset $PROJECT_ID:ccai_insights_data

# Export via the API
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "bigQueryDestination": {
      "projectId": "'"$PROJECT_ID"'",
      "dataset": "ccai_insights_data",
      "table": "conversations"
    },
    "writeDisposition": "WRITE_TRUNCATE"
  }' \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/insightsdata:export"
```

### Step 10.3: Query Turn-Level Sentiment in BigQuery

Once exported, the BigQuery table contains **nested sentence-level data** with sentiment scores.

**Query: Turn-by-turn sentiment for all conversations**

```sql
SELECT
  conversationName,
  sentences.sentimentScore AS turn_sentiment_score,
  sentences.sentimentMagnitude AS turn_sentiment_magnitude,
  sentences.speakerTag AS speaker,
  sentences.text AS turn_text,
  CASE
    WHEN sentences.sentimentScore >= 0.5 THEN 'POSITIVE'
    WHEN sentences.sentimentScore >= 0.25 THEN 'SOMEWHAT_POSITIVE'
    WHEN sentences.sentimentScore > -0.25 THEN 'NEUTRAL_OR_MIXED'
    WHEN sentences.sentimentScore > -0.5 THEN 'SOMEWHAT_NEGATIVE'
    ELSE 'NEGATIVE'
  END AS sentiment_label
FROM
  `your-project-id.ccai_insights_data.conversations`,
  UNNEST(sentences) AS sentences
ORDER BY
  conversationName,
  sentences.startOffsetNanos ASC;
```

**Query: Average customer sentiment per conversation**

```sql
SELECT
  conversationName,
  clientSentimentScore AS overall_customer_sentiment,
  clientSentimentMagnitude AS customer_sentiment_strength,
  agentSentimentScore AS overall_agent_sentiment,
  CASE
    WHEN clientSentimentScore >= 0.5 THEN 'POSITIVE'
    WHEN clientSentimentScore > -0.5 THEN 'NEUTRAL'
    ELSE 'NEGATIVE'
  END AS customer_sentiment_label
FROM
  `your-project-id.ccai_insights_data.conversations`
ORDER BY
  clientSentimentScore ASC;
```

**Query: Find conversations where sentiment shifts from negative to positive**

```sql
WITH turn_sentiments AS (
  SELECT
    conversationName,
    sentences.sentimentScore AS score,
    sentences.speakerTag AS speaker,
    ROW_NUMBER() OVER (
      PARTITION BY conversationName
      ORDER BY sentences.startOffsetNanos ASC
    ) AS turn_number,
    COUNT(*) OVER (PARTITION BY conversationName) AS total_turns
  FROM
    `your-project-id.ccai_insights_data.conversations`,
    UNNEST(sentences) AS sentences
  WHERE
    sentences.speakerTag = 1  -- Customer turns only
),
first_last AS (
  SELECT
    conversationName,
    MIN(CASE WHEN turn_number = 1 THEN score END) AS first_turn_sentiment,
    MAX(CASE WHEN turn_number = total_turns THEN score END) AS last_turn_sentiment
  FROM turn_sentiments
  GROUP BY conversationName
)
SELECT
  conversationName,
  first_turn_sentiment,
  last_turn_sentiment,
  last_turn_sentiment - first_turn_sentiment AS sentiment_shift
FROM first_last
WHERE first_turn_sentiment < 0 AND last_turn_sentiment > 0
ORDER BY sentiment_shift DESC;
```

**Query: Identify the most negative customer moments across all calls**

```sql
SELECT
  conversationName,
  sentences.text AS customer_statement,
  sentences.sentimentScore AS sentiment_score,
  sentences.sentimentMagnitude AS sentiment_magnitude
FROM
  `your-project-id.ccai_insights_data.conversations`,
  UNNEST(sentences) AS sentences
WHERE
  sentences.speakerTag = 1  -- Customer only
  AND sentences.sentimentScore <= -0.5
ORDER BY
  sentences.sentimentScore ASC,
  sentences.sentimentMagnitude DESC
LIMIT 100;
```

### BigQuery Schema — Key Sentiment Columns (V13)

| Column | Type | Description |
|--------|------|-------------|
| `agentSentimentScore` | FLOAT | Agent sentiment: -1.0 (negative) to 1.0 (positive) |
| `agentSentimentMagnitude` | FLOAT | Absolute magnitude of agent sentiment |
| `clientSentimentScore` | FLOAT | Customer sentiment: -1.0 (negative) to 1.0 (positive) |
| `clientSentimentMagnitude` | FLOAT | Absolute magnitude of customer sentiment |
| `clientSentimentRationale` | STRING | Explanation for client sentiment assessment |
| `sentences.sentimentScore` | FLOAT | Per-sentence/turn sentiment score |
| `sentences.sentimentMagnitude` | FLOAT | Per-sentence/turn sentiment magnitude |
| `sentences.speakerTag` | INTEGER | Speaker identifier (1 = customer, 2 = agent) |
| `sentences.text` | STRING | The text of the turn |
| `sentences.startOffsetNanos` | INTEGER | Start time of the turn |
| `sentences.endOffsetNanos` | INTEGER | End time of the turn |
| `entities.sentimentScore` | FLOAT | Entity-level sentiment |
| `entities.sentimentMagnitude` | FLOAT | Entity-level sentiment magnitude |

---

## 11. All CCAI Insights Features Overview

Beyond sentiment analysis, here is a summary of everything CCAI Insights can do when you analyze a conversation:

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Sentiment Analysis** | Per-turn and conversation-level emotional scoring | Track customer satisfaction, identify frustration points |
| **Topic/Issue Detection** | ML-based classification of conversation topics | Find top call drivers, categorize interactions |
| **Entity Extraction** | Identifies products, dates, locations, people, etc. | Product mention tracking, data extraction |
| **Intent Detection** | Determines what the customer is trying to accomplish | Route calls, understand needs |
| **Silence Detection** | Flags periods of silence in voice conversations | Identify hold times, dead air |
| **Interruption Detection** | Detects when speakers talk over each other | Agent coaching, quality monitoring |
| **Conversation Summary** | Auto-generated summary of the conversation | Quick review, CRM logging |
| **Phrase Matching** | Custom keyword/phrase detection | Compliance monitoring, script adherence |
| **Quality AI / Scorecards** | Agent evaluation against custom criteria | Quality assurance, coaching |
| **Data Redaction** | PII/sensitive data removal via DLP integration | Privacy compliance |
| **BigQuery Export** | Export all data for custom analytics | Dashboards, trend analysis |
| **Looker Integration** | Pre-built dashboards for visualization | Operational reporting |

---

## 12. Pricing

CCAI Insights pricing (as of early 2026 — check [the official pricing page](https://cloud.google.com/contact-center/insights/pricing) for current rates):

| Tier | Chat | Voice |
|------|------|-------|
| **Standard** | $0.0015 per message | $0.015 per minute |
| **Enterprise** | $0.0025 per message | $0.025 per minute |

Additional costs may apply for:
- Cloud Storage (storing transcripts/audio)
- Speech-to-Text (if auto-transcribing audio)
- BigQuery (if exporting data)
- Cloud DLP (if using data redaction)

---

## 13. Troubleshooting

### "Audio must have exactly two channels"

Voice recordings must be dual-channel (stereo) audio. Mono or multi-channel audio is not supported. Convert your audio:

```bash
# Convert mono to stereo with ffmpeg
ffmpeg -i input_mono.wav -ac 2 output_stereo.wav
```

### "Transcript format not supported"

Voice transcripts must match the Cloud Speech-to-Text API response format. Chat transcripts must follow the CCAI conversation data format (JSON with `entries[]`).

### "Permission denied" errors

Ensure your account or service account has the required IAM roles:
- `roles/contactcenterinsights.editor`
- `roles/storage.admin` (for GCS access)
- `roles/speech.admin` (for Speech-to-Text)

```bash
# Check your current permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_EMAIL"
```

### Analysis takes too long

- Single conversation analysis typically completes in 1-2 minutes
- Bulk analysis duration depends on the number of conversations
- Use the Operations API to check status:

```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/operations/$OPERATION_ID"
```

### "API not enabled" errors

Run the API enablement command from [Step 3.3](#step-33-enable-required-apis):

```bash
gcloud services enable contactcenterinsights.googleapis.com
```

### Only English is supported

As of early 2026, sentiment analysis in CX Insights supports English dialects only. The language code is auto-inferred if not explicitly provided.

---

## 14. Resources & Links

### Official Documentation
- [CX Insights Overview](https://docs.cloud.google.com/contact-center/insights/docs)
- [Sentiment Analysis Guide](https://docs.cloud.google.com/contact-center/insights/docs/sentiment-analysis)
- [Analyze a Conversation (API)](https://docs.cloud.google.com/contact-center/insights/docs/create-analyze-conversation-api)
- [Import Conversations (API)](https://cloud.google.com/contact-center/insights/docs/ingest-conversations-api)
- [Import Conversations (Console)](https://docs.cloud.google.com/contact-center/insights/docs/create-analyze-conversation-ui)
- [Conversation Data Format](https://docs.cloud.google.com/contact-center/insights/docs/conversation-data-format)
- [REST API Reference](https://docs.cloud.google.com/contact-center/insights/docs/reference/rest)
- [BigQuery Export](https://cloud.google.com/contact-center/insights/docs/export)
- [BigQuery V13 Schema](https://docs.cloud.google.com/contact-center/insights/docs/bigquery-v13-schema)
- [Release Notes](https://cloud.google.com/contact-center/insights/docs/release-notes)

### Client Libraries
- [Python Library (PyPI)](https://pypi.org/project/google-cloud-contact-center-insights/)
- [Python API Reference](https://docs.cloud.google.com/python/docs/reference/contactcenterinsights/latest/google.cloud.contact_center_insights_v1.services.contact_center_insights.ContactCenterInsightsClient)
- [Node.js Library](https://www.npmjs.com/package/@google-cloud/contact-center-insights)
- [CX Insights DevKit](https://docs.cloud.google.com/contact-center/insights/docs/python-library-for-developers)
- [GitHub Samples](https://github.com/GoogleCloudPlatform/contact-center-ai-samples)

### Community Guides
- [10-Minute Demo Guide (Medium)](https://medium.com/google-cloud/unlock-conversational-ai-a-10-minute-demo-guide-for-google-cloud-contact-center-insights-6e005d7662cf)
- [Quick Guide to CCAI Insights (Medium)](https://medium.com/google-cloud/supercharge-your-contact-center-analysis-a-quick-guide-to-using-gcps-ccai-insights-platform-985f40fe59fa)
- [Analyze Call Center Conversations Series (Medium)](https://medium.com/google-cloud/analyze-call-center-conversations-using-google-cloud-conversational-insights-part-3-d372f1bcf79f)
- [Conversational Insights Training (Cloud Skills Boost)](https://www.cloudskillsboost.google/course_templates/1123)

### CX Insights Console
- [Direct Console Access](https://ccai.cloud.google.com/insights/projects)
- [Looker Block for CCAI Insights](https://marketplace.looker.com/marketplace/detail/ccai-insights)
