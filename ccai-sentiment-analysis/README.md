# Turn-by-Turn Sentiment Analysis with Google Cloud CCAI Insights

## A Complete, Copy-Paste Beginner's Guide

> **Brand new to Google Cloud?** Start with [GETTING_STARTED.md](./GETTING_STARTED.md) instead. It walks you through creating an account, setting up a project, and running your first analysis — assuming zero prior experience.

This project gives you **5 different ways** to perform turn-by-turn sentiment analysis on contact center conversations using [Google Cloud Customer Experience Insights](https://cloud.google.com/solutions/ccai-insights) (formerly CCAI Insights / Conversational Insights).

Every method is self-contained with runnable code. Pick the one that fits your needs.

---

## Quick Start: Which Method Should I Use?

| Method | Best For | Skill Level | Time |
|--------|----------|-------------|------|
| [Method 1: Console](#method-1-console-ui) | Visual exploration, one-off analysis | Beginner | 10 min |
| [Method 2: curl](#method-2-rest-api-with-curl) | Shell scripting, CI/CD, no Python | Beginner | 15 min |
| [Method 3: Python Client](#method-3-python-client-library) | Production apps, automation | Intermediate | 20 min |
| [Method 4: DevKit](#method-4-cx-insights-devkit) | Audio transcription, format conversion | Intermediate | 25 min |
| [Method 5: BigQuery SQL](#method-5-bigquery-sql-export) | Large-scale analytics, dashboards | Intermediate | 20 min |

---

## What's In This Project

```
ccai-sentiment-analysis/
├── GETTING_STARTED.md                 # START HERE if new to Google Cloud
├── README.md                          # This file (full reference guide)
├── requirements.txt                   # Python dependencies
├── sample_conversation.json           # Sample data (a 10-turn support chat)
├── 00_setup.sh                        # One-time prerequisites setup
├── method1_console_walkthrough.md     # Step-by-step browser guide
├── method2_curl_pipeline.sh           # End-to-end curl script
├── method3_python_client.py           # Python client library script
├── method4_devkit.py                  # CX Insights DevKit script
├── method5_bigquery_export.sh         # BigQuery export setup script
└── method5_bigquery_queries.sql       # 10 ready-to-use SQL queries
```

---

## Prerequisites (Do This First)

Before using ANY method, you need a Google Cloud project with the right APIs enabled and a sample conversation uploaded to Cloud Storage.

### Option A: Run the Setup Script (Recommended)

> **Tip: Use Google Cloud Shell** — it's a free terminal in your browser with all tools pre-installed. Click the `>_` icon at the top-right of the [Cloud Console](https://console.cloud.google.com). See [GETTING_STARTED.md](./GETTING_STARTED.md) for a full walkthrough.

```bash
# 1. Edit the 2 variables at the top of 00_setup.sh.
#    The quickest way (replace the placeholder values with your own):
sed -i 's/your-project-id/MY-ACTUAL-PROJECT-ID/g' 00_setup.sh
sed -i 's/your-bucket-name/my-unique-bucket-12345/g' 00_setup.sh

#    Or open in an editor:  cloudshell edit 00_setup.sh
#    Or in terminal:        nano 00_setup.sh

# 2. Make it executable and run it:
chmod +x 00_setup.sh
./00_setup.sh
```

> **Where to find your Project ID:** Click the project dropdown at the top of the Cloud Console. The Project ID is the grey text under the project name (e.g., `my-project-438291`).

The script will:
1. Authenticate you with Google Cloud
2. Set your project
3. Enable all 6 required APIs
4. Create a Cloud Storage bucket
5. Upload the sample conversation
6. Optionally install Python dependencies

### Option B: Manual Setup

If you prefer to set things up by hand:

```bash
# Step 1: Install the Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Step 2: Authenticate
gcloud auth login
gcloud auth application-default login

# Step 3: Set your project
gcloud config set project YOUR_PROJECT_ID

# Step 4: Enable APIs
gcloud services enable \
  contactcenterinsights.googleapis.com \
  speech.googleapis.com \
  storage.googleapis.com \
  dlp.googleapis.com \
  language.googleapis.com \
  bigquery.googleapis.com

# Step 5: Create a bucket
gcloud storage buckets create gs://YOUR_BUCKET_NAME \
  --location=us-central1 \
  --default-storage-class=STANDARD

# Step 6: Upload the sample conversation
gcloud storage cp sample_conversation.json \
  gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json

# Step 7 (for Methods 3/4/5): Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## The Sample Conversation

The file `sample_conversation.json` contains a 10-turn customer support chat about an internet outage. The customer starts frustrated and ends satisfied after receiving a credit. This makes it ideal for demonstrating sentiment shifts.

**Conversation summary:**
- Customer: Reports 3-day internet outage, threatens to switch providers
- Agent: Troubleshoots, schedules a technician, proactively offers a billing credit
- Customer: Appreciates the help, sentiment turns positive

**Expected sentiment arc:**

```
Turn 1 (Customer): "really frustrating"                    → Somewhat Negative (-0.5)
Turn 3 (Customer): "terrible...considering switching"      → Negative (-1.0)
Turn 5 (Customer): "affecting my job"                      → Somewhat Negative (-0.5)
Turn 7 (Customer): "should get a credit"                   → Mixed (-0.25)
Turn 9 (Customer): "appreciate you...thank you"            → Positive (+1.0)
```

---

## How Sentiment Scoring Works

CX Insights gives each customer turn two numbers:

- **Score** (-1.0 to +1.0): How positive or negative the statement is
- **Magnitude** (0.0 to infinity): How strong the emotion is

### Turn-Level Labels

| Score | Magnitude | Label | Category |
|-------|-----------|-------|----------|
| -1.0 | 1.0 | `negative` | Negative |
| -0.5 | 0.5 | `somewhat_negative` | Negative |
| -0.25 | 0.75 | `mixed_more_negative` | Negative |
| 0.0 | 0.0 | `neutral` | Neutral |
| 0.0 | 0.75 | `mixed_balanced` | Neutral |
| +0.25 | 0.75 | `mixed_more_positive` | Positive |
| +0.5 | 0.5 | `somewhat_positive` | Positive |
| +1.0 | 1.0 | `positive` | Positive |

### Conversation-Level Labels

| Score Range | Label |
|-------------|-------|
| >= 0.5 | Positive |
| -0.5 to 0.5 | Neutral |
| <= -0.5 | Negative |

---

## Method 1: Console UI

**No code required.** Everything happens in your browser.

### Steps

1. Open the CX Insights console: https://console.cloud.google.com/contact-center/insights
2. Select your project
3. Click **Conversation Hub** in the left sidebar
4. Click **Import** > **Chat** > **File**
5. Enter the transcript URI: `gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json`
6. Enter Agent ID: `agent-001`, click **Import**
7. Click the imported conversation to open it
8. Click **Analyze** and wait 1-2 minutes
9. Scroll to **Conversation spotlight** to see turn-by-turn sentiment

**Detailed walkthrough:** Open [`method1_console_walkthrough.md`](./method1_console_walkthrough.md) for full step-by-step instructions with expected results.

---

## Method 2: REST API with curl

**No Python required.** A single shell script that does everything.

### Prerequisites
- `jq` installed (`sudo apt-get install jq` or `brew install jq`)

### Steps

```bash
# 1. Open method2_curl_pipeline.sh and edit the 3 variables:
#    PROJECT_ID, LOCATION, BUCKET_NAME

# 2. Make it executable and run it:
chmod +x method2_curl_pipeline.sh
./method2_curl_pipeline.sh
```

### What It Does

The script runs 5 steps automatically:

1. **Uploads** the conversation to CX Insights via `POST .../conversations:upload`
2. **Polls** the upload operation until complete
3. **Creates an analysis** via `POST .../conversations/{id}/analyses` with all annotators
4. **Polls** the analysis operation until complete
5. **Retrieves** and displays results including:
   - Conversation-level sentiment
   - Turn-by-turn sentiment annotations
   - Entity extraction
   - Intent detection
   - Issue/topic detection

### Output

Results are saved to `results_method2.json`. The script also prints a **cheat sheet** of individual curl commands you can run manually.

### Key curl Commands (for reference)

```bash
# Upload a conversation:
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"conversation":{"dataSource":{"gcsSource":{"transcriptUri":"gs://BUCKET/transcripts/file.json"}},"medium":"CHAT"}}' \
  "https://contactcenterinsights.googleapis.com/v1/projects/PROJECT/locations/LOCATION/conversations:upload"

# Analyze with sentiment only:
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"annotatorSelector":{"runSentimentAnnotator":true}}' \
  "https://contactcenterinsights.googleapis.com/v1/projects/PROJECT/locations/LOCATION/conversations/CONV_ID/analyses"

# Analyze with ALL annotators (default):
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://contactcenterinsights.googleapis.com/v1/projects/PROJECT/locations/LOCATION/conversations/CONV_ID/analyses"

# Get conversation with results:
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/PROJECT/locations/LOCATION/conversations/CONV_ID"

# Filter sentiment annotations from results with jq:
cat results.json | jq '.latestAnalysis.analysisResult.callAnalysisMetadata.annotations[] | select(.sentimentData != null)'
```

### Annotator Selector Reference

When creating an analysis, you can control which annotators run:

```json
{
  "annotatorSelector": {
    "runSentimentAnnotator": true,
    "runEntityAnnotator": true,
    "runIntentAnnotator": true,
    "runSilenceAnnotator": true,
    "runInterruptionAnnotator": true,
    "runIssueModelAnnotator": true,
    "runPhraseMatcherAnnotator": true
  }
}
```

Send an empty body `{}` to run ALL annotators by default.

---

## Method 3: Python Client Library

**The most flexible approach.** A full-featured Python script with CLI flags.

### Steps

```bash
# 1. Install dependencies:
pip install -r requirements.txt

# 2. Authenticate:
gcloud auth application-default login

# 3. Open method3_python_client.py and edit the 3 variables:
#    PROJECT_ID, LOCATION, BUCKET_NAME

# 4. Run the full pipeline:
python method3_python_client.py
```

### CLI Options

```bash
# Full pipeline (upload + analyze + display all features):
python method3_python_client.py

# Sentiment annotator only (faster, skip entity/intent/etc.):
python method3_python_client.py --sentiment-only

# Analyze an existing conversation (skip upload):
python method3_python_client.py --analyze CONVERSATION_ID

# Bulk analyze all conversations in the project:
python method3_python_client.py --bulk

# List all conversations:
python method3_python_client.py --list
```

### What It Does

The script runs 4 steps:

1. **Uploads** the conversation using `UploadConversationRequest`
2. **Analyzes** it using `create_analysis()` (all annotators by default)
3. **Retrieves** the conversation with `get_conversation()`
4. **Displays** results in formatted tables:
   - Turn-by-turn sentiment (with scores, magnitudes, and labels)
   - Conversation-level sentiment (customer + agent)
   - Entities extracted
   - Intents detected
   - Issues/topics classified
   - Annotation summary (counts by type)

### Key Code Patterns

```python
from google.cloud import contact_center_insights_v1

client = contact_center_insights_v1.ContactCenterInsightsClient()

# Upload a conversation
conversation = contact_center_insights_v1.Conversation()
conversation.data_source.gcs_source.transcript_uri = "gs://bucket/transcript.json"
conversation.medium = contact_center_insights_v1.Conversation.Medium.CHAT

request = contact_center_insights_v1.UploadConversationRequest(
    parent="projects/PROJECT/locations/LOCATION",
    conversation=conversation,
)
operation = client.upload_conversation(request=request)
result = operation.result(timeout=600)  # Returns Conversation object

# Analyze (all annotators)
analysis = contact_center_insights_v1.Analysis()
operation = client.create_analysis(parent=result.name, analysis=analysis)
analysis_result = operation.result(timeout=86400)  # Returns Analysis object

# Analyze (sentiment only)
analysis = contact_center_insights_v1.Analysis()
analysis.annotator_selector.run_sentiment_annotator = True
operation = client.create_analysis(parent=result.name, analysis=analysis)

# Get results
conversation = client.get_conversation(name=result.name)
metadata = conversation.latest_analysis.analysis_result.call_analysis_metadata

# Per-turn sentiment
for annotation in metadata.annotations:
    if annotation.sentiment_data:
        print(f"Channel {annotation.channel_tag}: "
              f"score={annotation.sentiment_data.score}, "
              f"magnitude={annotation.sentiment_data.magnitude}")

# Conversation-level sentiment
for sentiment in metadata.sentiments:
    print(f"Channel {sentiment.channel_tag}: "
          f"score={sentiment.sentiment_data.score}")
```

---

## Method 4: CX Insights DevKit

**Best for audio files and platform migrations.** A higher-level Python library from Google.

### When to Use This

- You have **audio recordings** that need transcription first
- You need **role recognition** (auto-detect who is agent vs. customer)
- You are migrating from **Genesys Cloud** or **AWS Connect** and need format conversion
- You want a simplified API for bulk operations

### Steps

```bash
# 1. Get the DevKit (check the official docs for the latest location):
#    https://docs.cloud.google.com/contact-center/insights/docs/python-library-for-developers

# 2. Install its dependencies:
pip install -r requirements.txt

# 3. Authenticate:
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 4. Edit method4_devkit.py variables (PROJECT_ID, BUCKET_NAME)

# 5. Run with a workflow:
python method4_devkit.py --workflow chat      # Ingest a chat transcript
python method4_devkit.py --workflow audio     # Transcribe + ingest audio
python method4_devkit.py --workflow convert   # See format conversion examples
python method4_devkit.py --workflow bigquery  # See BigQuery setup via DevKit
python method4_devkit.py --workflow all       # Show all workflows
```

### Audio Pipeline (What It Does)

```
Audio file (.wav)
    → Speech-to-Text V2 transcription
    → Format to CX Insights JSON
    → Role recognition (agent vs. customer)
    → Upload to Cloud Storage
    → Ingest into CX Insights
    → Ready for analysis
```

### Fallback

If the DevKit is not installed, the script **falls back** to the standard Python client library (Method 3) for the chat workflow. It also prints the DevKit code so you can see what it would look like.

---

## Method 5: BigQuery SQL Export

**Best for large-scale analysis across many conversations.** Export everything to BigQuery, then run SQL.

### Steps

```bash
# Part 1: Export data to BigQuery

# 1. Make sure you have at least one analyzed conversation
#    (from Method 1, 2, 3, or 4)

# 2. Edit method5_bigquery_export.sh variables

# 3. Run:
chmod +x method5_bigquery_export.sh
./method5_bigquery_export.sh

# Part 2: Run SQL queries

# 4. Open the BigQuery console:
#    https://console.cloud.google.com/bigquery

# 5. Open method5_bigquery_queries.sql

# 6. Copy any query, replace YOUR_PROJECT_ID and YOUR_DATASET, and run it
```

### Available Queries (10 total)

| # | Query | What It Shows |
|---|-------|---------------|
| 1 | Turn-by-turn sentiment (all) | Every turn with score + label |
| 2 | Customer-only turns | Only customer messages with sentiment |
| 3 | Conversation-level summary | One row per conversation |
| 4 | Sentiment distribution | % positive/neutral/negative |
| 5 | Sentiment shift detection | Conversations that went negative→positive |
| 6 | Most negative moments | Top customer complaints |
| 7 | Most positive moments | Top customer praise |
| 8 | Sentiment trend | Turn-by-turn with rolling average |
| 9 | Entity sentiment | Sentiment about specific products/topics |
| 10 | Complete report | All metrics in one row per conversation |

### Key BigQuery Columns

| Column | Type | Description |
|--------|------|-------------|
| `clientSentimentScore` | FLOAT | Overall customer sentiment (-1.0 to 1.0) |
| `clientSentimentMagnitude` | FLOAT | Strength of customer sentiment |
| `clientSentimentRationale` | STRING | Why the system assigned that score |
| `agentSentimentScore` | FLOAT | Overall agent sentiment |
| `sentences.sentimentScore` | FLOAT | Per-turn sentiment score |
| `sentences.sentimentMagnitude` | FLOAT | Per-turn sentiment magnitude |
| `sentences.speakerTag` | INT | 1=customer, 2=agent |
| `sentences.text` | STRING | The text of the turn |
| `entities.sentimentScore` | FLOAT | Sentiment about a specific entity |

---

## Analysis Results Structure

When you retrieve an analysis (via any method), the results are organized like this:

```
Analysis
└── analysisResult
    └── callAnalysisMetadata
        │
        ├── annotations[]                     ← Per-turn annotations
        │   ├── sentimentData                 ← Turn sentiment
        │   │   ├── score                     ← -1.0 to +1.0
        │   │   └── magnitude                 ← 0.0 to infinity
        │   ├── entityMentionData             ← Entity mentions
        │   ├── intentMatchData               ← Intent matches
        │   ├── silenceData                   ← Silence periods
        │   ├── interruptionData              ← Interruptions
        │   ├── channelTag                    ← 1=customer, 2=agent
        │   ├── annotationStartBoundary       ← Where in transcript
        │   └── annotationEndBoundary
        │
        ├── sentiments[]                      ← Conversation-level
        │   ├── channelTag
        │   └── sentimentData { score, magnitude }
        │
        ├── entities{}                        ← Extracted entities
        ├── intents{}                         ← Detected intents
        └── issueModelResult                  ← Topic classification
```

---

## All CCAI Insights Features

| Feature | Annotator Flag | Description |
|---------|---------------|-------------|
| Sentiment Analysis | `runSentimentAnnotator` | Per-turn + conversation-level emotion scoring |
| Entity Extraction | `runEntityAnnotator` | Products, dates, amounts, names |
| Intent Detection | `runIntentAnnotator` | What the customer wants to do |
| Silence Detection | `runSilenceAnnotator` | Dead air periods (voice only) |
| Interruption Detection | `runInterruptionAnnotator` | Talking over each other (voice only) |
| Issue/Topic Detection | `runIssueModelAnnotator` | ML-based topic classification |
| Phrase Matching | `runPhraseMatcherAnnotator` | Custom keyword/phrase detection |
| Conversation Summary | (automatic) | Auto-generated conversation summary |
| Quality AI / Scorecards | (console) | Agent evaluation against criteria |
| Data Redaction | (settings) | PII removal via Cloud DLP |

---

## Troubleshooting

### "API not enabled"
```bash
gcloud services enable contactcenterinsights.googleapis.com
```

### "Permission denied"
```bash
# Check your roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_EMAIL"

# You need: roles/contactcenterinsights.editor
```

### "Audio must have exactly two channels"
```bash
# Convert mono to stereo
ffmpeg -i input_mono.wav -ac 2 output_stereo.wav
```

### "Transcript format not supported"
Make sure your JSON has the exact structure: `{ "entries": [ { "text", "role", "user_id", "start_timestamp_usec" } ] }`

### Analysis times out
Single conversations take 1-2 minutes. Bulk analysis depends on volume. Poll the operation:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://contactcenterinsights.googleapis.com/v1/projects/PROJECT/locations/LOCATION/operations/OP_ID"
```

### Only English supported
As of early 2026, CX Insights sentiment analysis supports English dialects only.

---

## Pricing

| Tier | Chat | Voice |
|------|------|-------|
| Standard | $0.0015/message | $0.015/minute |
| Enterprise | $0.0025/message | $0.025/minute |

Check the [official pricing page](https://cloud.google.com/contact-center/insights/pricing) for current rates. Additional costs apply for Cloud Storage, Speech-to-Text, BigQuery, and Cloud DLP.

---

## Resources

### Official Documentation
- [CX Insights Overview](https://docs.cloud.google.com/contact-center/insights/docs)
- [Sentiment Analysis Guide](https://docs.cloud.google.com/contact-center/insights/docs/sentiment-analysis)
- [Analyze a Conversation (API)](https://docs.cloud.google.com/contact-center/insights/docs/create-analyze-conversation-api)
- [Import Conversations (API)](https://cloud.google.com/contact-center/insights/docs/ingest-conversations-api)
- [Conversation Data Format](https://docs.cloud.google.com/contact-center/insights/docs/conversation-data-format)
- [REST API Reference](https://docs.cloud.google.com/contact-center/insights/docs/reference/rest)
- [BigQuery V13 Schema](https://docs.cloud.google.com/contact-center/insights/docs/bigquery-v13-schema)

### Client Libraries
- [Python (PyPI)](https://pypi.org/project/google-cloud-contact-center-insights/)
- [Python API Reference](https://docs.cloud.google.com/python/docs/reference/contactcenterinsights/latest)
- [Node.js](https://www.npmjs.com/package/@google-cloud/contact-center-insights)
- [CX Insights DevKit](https://docs.cloud.google.com/contact-center/insights/docs/python-library-for-developers)
- [GitHub Samples](https://github.com/GoogleCloudPlatform/contact-center-ai-samples)

### Community Guides
- [10-Minute Demo Guide (Medium)](https://medium.com/google-cloud/unlock-conversational-ai-a-10-minute-demo-guide-for-google-cloud-contact-center-insights-6e005d7662cf)
- [Quick Guide to CCAI Insights (Medium)](https://medium.com/google-cloud/supercharge-your-contact-center-analysis-a-quick-guide-to-using-gcps-ccai-insights-platform-985f40fe59fa)
- [Analyzing Call Center Conversations (Medium)](https://medium.com/google-cloud/analyze-call-center-conversations-using-google-cloud-conversational-insights-part-3-d372f1bcf79f)
