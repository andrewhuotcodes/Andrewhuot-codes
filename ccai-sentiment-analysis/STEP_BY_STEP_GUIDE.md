# CCAI Insights: Complete Step-by-Step Guide

## Run Everything From Start to Finish

This is a single, linear document. Follow it from top to bottom and you will set up Google Cloud, run every method, and see turn-by-turn sentiment analysis results. Every command is copy-paste ready.

**What you will need:**
- A web browser (Chrome recommended)
- A Google account (Gmail works)
- A credit card (Google gives you $300 free credits — you will not be charged)

**What you will do:**
1. Create a Google Cloud account and project
2. Open Cloud Shell (a free terminal in your browser)
3. Download the project files
4. Run the setup script (enables APIs, creates storage, uploads sample data)
5. Run Method 1: Console UI (point-and-click in the browser)
6. Run Method 2: curl/REST API (terminal commands, no Python)
7. Run Method 3: Python Client Library (Python script with formatted tables)
8. Run Method 4: DevKit (advanced — audio files and format conversion)
9. Run Method 5: BigQuery SQL (SQL queries for dashboards and reporting)

---

## PHASE 1: ONE-TIME SETUP

---

### Step 1: Create a Google Cloud Account

> Already have one? Skip to [Step 2](#step-2-create-a-project).

1. Open your browser and go to **https://cloud.google.com**
2. Click **"Get started for free"** (blue button)
3. Sign in with your Google (Gmail) account
4. Enter your billing information (credit card required, but you get **$300 free credits** for 90 days)
5. Accept the terms of service and click **Start my free trial**

You are now in the **Google Cloud Console**.

---

### Step 2: Create a Project

1. At the top of the console, click the **project dropdown** (says "Select a project" or "My First Project")
2. Click **New Project** (top-right of the popup)
3. **Project name:** type `ccai-insights-demo`
4. Click **Create**
5. Wait 10-20 seconds

Now find your **Project ID** — this is the most important value:

1. Click the project dropdown at the top again
2. You will see two things:
   - **Project name:** `ccai-insights-demo` (what you typed)
   - **Project ID:** something like `ccai-insights-demo-438291` (auto-generated, with numbers)
3. **Copy the Project ID** (the one with numbers). Write it down.
4. Click on your project to select it

> **Throughout this guide**, whenever you see `YOUR_PROJECT_ID`, replace it with your actual Project ID (e.g., `ccai-insights-demo-438291`).
>
> Whenever you see `YOUR_BUCKET_NAME`, replace it with a unique bucket name you choose (e.g., `my-ccai-bucket-73921`). Add random numbers to make it unique.

---

### Step 3: Open Cloud Shell

Cloud Shell is a free Linux terminal in your browser. It has everything pre-installed (`gcloud`, `jq`, `python3`).

1. Look at the **top-right** of the Google Cloud Console
2. Click the icon that looks like a terminal: **`>_`**
3. A black terminal panel opens at the bottom of the screen
4. Wait for it to show a prompt like `yourname@cloudshell:~$`

Test it:

```bash
echo "Cloud Shell is working!"
```

You should see `Cloud Shell is working!` printed back.

---

### Step 4: Download the Project Files

Pick one option:

**Option A — Clone from Git (if files are in a repository):**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/ccai-sentiment-analysis
```

**Option B — Upload manually:**

1. In Cloud Shell, click the three-dot menu (**...**) at the top of the terminal
2. Click **Upload** > **Folder**
3. Select the `ccai-sentiment-analysis/` folder from your computer
4. Navigate to it:

```bash
cd ~/ccai-sentiment-analysis
```

**Verify the files are there:**

```bash
ls -la
```

You should see these files:

```
00_setup.sh
GETTING_STARTED.md
README.md
STEP_BY_STEP_GUIDE.md
method1_console_walkthrough.md
method2_curl_pipeline.sh
method3_python_client.py
method4_devkit.py
method5_bigquery_export.sh
method5_bigquery_queries.sql
requirements.txt
sample_conversation.json
```

---

### Step 5: Edit and Run the Setup Script

The setup script enables APIs, creates a storage bucket, and uploads the sample conversation.

**Step 5a: Put your values into the script.**

Run these two commands, replacing the placeholder values with your own:

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' 00_setup.sh
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' 00_setup.sh
```

**Concrete example** (if your Project ID is `ccai-insights-demo-438291` and you pick bucket name `my-ccai-bucket-73921`):

```bash
sed -i 's/your-project-id/ccai-insights-demo-438291/g' 00_setup.sh
sed -i 's/your-bucket-name/my-ccai-bucket-73921/g' 00_setup.sh
```

**Step 5b: Run it.**

```bash
chmod +x 00_setup.sh
./00_setup.sh
```

**What you will see:**

```
============================================================
  CCAI Insights: Prerequisites Setup
============================================================

  Step 1/6: Authentication
  You are logged in as: your.email@gmail.com

  Step 2/6: Setting project to ccai-insights-demo-438291
  Step 3/6: Enabling required APIs (this may take a minute)
  Step 4/6: Creating Cloud Storage bucket
  Step 5/6: Uploading sample conversation to Cloud Storage
  Step 6/6: Python dependencies (optional)
  Install Python dependencies now? (y/n):
```

**Type `y` and press Enter.** This installs the Python libraries needed for Methods 3, 4, and 5.

**Step 5c: Confirm success.**

At the end you should see:

```
============================================================
  SETUP COMPLETE
============================================================

  Project:     ccai-insights-demo-438291
  Bucket:      gs://my-ccai-bucket-73921
  Transcript:  gs://my-ccai-bucket-73921/transcripts/sample_conversation.json
```

**Save these three values.** You will use them in every method below.

> **Error?** The most common error is `ERROR 403: billing not enabled`. Go to https://console.cloud.google.com/billing and link billing to your project.

---

## PHASE 2: RUN ALL 5 METHODS

You are now fully set up. Below are all 5 methods, run in order. Each one analyzes the same sample conversation in a different way.

---

## METHOD 1: Console UI (Browser, No Code)

**Time:** 10 minutes
**What this does:** Import and analyze the conversation using only the browser. No terminal commands needed.

---

### M1 — Step 1: Open the CX Insights Console

Open this URL in your browser:

```
https://console.cloud.google.com/contact-center/insights
```

If prompted, select your project from the dropdown at the top.

---

### M1 — Step 2: Navigate to Conversation Hub

1. In the left sidebar, click **Conversation Hub**
2. The list will be empty (this is your first time)

---

### M1 — Step 3: Import the Sample Conversation

1. Click the **Import** button
2. Select **Chat** (our sample is a text transcript)
3. Click **Next**
4. Select **File**
5. In the **Transcript URI** field, paste:

```
gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json
```

(Replace `YOUR_BUCKET_NAME` with your actual bucket name, e.g., `gs://my-ccai-bucket-73921/transcripts/sample_conversation.json`)

6. Click **Next**
7. Set **Agent ID** to: `agent-001`
8. Set **Agent display name** to: `Support Agent`
9. Click **Import**
10. Wait 10-30 seconds for the import to complete

---

### M1 — Step 4: Analyze the Conversation

1. Your conversation now appears in the Conversation Hub list
2. Click on it to open it
3. You will see the transcript displayed as a chat — customer messages on one side, agent messages on the other
4. Click the **Analyze** button (at the top of the conversation)
5. Wait 1-2 minutes for the analysis to complete
6. The page will refresh automatically (or refresh manually)

---

### M1 — Step 5: View the Results

Scroll down to the **Conversation Spotlight** section. You will see:

- A **sentiment timeline chart** showing how sentiment changes across the conversation
- **Top positive moments** (highlighted in blue)
- **Top negative moments** (highlighted in red)

Hover over individual customer messages to see:
- **Sentiment score** (number from -1.0 to +1.0)
- **Sentiment label** (e.g., "negative", "somewhat_positive", "positive")

At the top of the page, you will see:
- **Overall customer sentiment** (aggregated score)
- **Overall agent sentiment** (aggregated score)

Click the **Information** tab for:
- Detected entities (products, amounts, account numbers)
- Detected issues/topics
- Intent classification

**Expected results for the sample conversation:**

| Turn | Speaker  | Message (abbreviated)               | Expected Sentiment |
|------|----------|-------------------------------------|--------------------|
| 1    | Customer | "problems...really frustrating"     | Somewhat Negative  |
| 2    | Agent    | "sorry to hear...happy to help"     | (not scored)       |
| 3    | Customer | "terrible...considering switching"  | Negative           |
| 4    | Agent    | "understand your frustration"       | (not scored)       |
| 5    | Customer | "affecting my job"                  | Somewhat Negative  |
| 6    | Agent    | "schedule a technician"             | (not scored)       |
| 7    | Customer | "should get a credit"               | Mixed              |
| 8    | Agent    | "applied a 5-day credit"            | (not scored)       |
| 9    | Customer | "appreciate you...thank you"        | Positive           |
| 10   | Agent    | "You're welcome!"                   | (not scored)       |

**Method 1 is done.** You saw sentiment analysis through the browser UI.

---

## METHOD 2: curl / REST API (Terminal, No Python)

**Time:** 5 minutes
**What this does:** Runs the entire pipeline from the terminal using `curl` commands. Uploads the conversation, runs analysis, waits for completion, and displays all results.

---

### M2 — Step 1: Edit the Script

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method2_curl_pipeline.sh
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method2_curl_pipeline.sh
```

**Concrete example:**

```bash
sed -i 's/your-project-id/ccai-insights-demo-438291/g' method2_curl_pipeline.sh
sed -i 's/your-bucket-name/my-ccai-bucket-73921/g' method2_curl_pipeline.sh
```

---

### M2 — Step 2: Run It

```bash
chmod +x method2_curl_pipeline.sh
./method2_curl_pipeline.sh
```

---

### M2 — Step 3: Watch It Run

The script will automatically:

1. **Upload** the conversation to CX Insights (Step 1/5)
2. **Wait** for the upload to complete by polling (Step 2/5)
3. **Analyze** the conversation with all annotators — sentiment, entities, intents, issues (Step 3/5)
4. **Wait** for the analysis to complete by polling (Step 4/5)
5. **Display** the full results (Step 5/5)

**What the output looks like:**

```
============================================================
  CCAI Insights: Method 2 — curl REST API Pipeline
============================================================

  STEP 1/5: Upload conversation to CX Insights
  Transcript: gs://my-ccai-bucket-73921/transcripts/sample_conversation.json

  STEP 2/5: Waiting for upload to complete
  Done! (after 3 polls)

  STEP 3/5: Analyzing conversation (all annotators)
  STEP 4/5: Waiting for analysis to complete
  Done! (after 5 polls)

  STEP 5/5: Retrieving full results

╔══════════════════════════════════════════════════════════════════════════════╗
║  CUSTOMER SENTIMENT JOURNEY                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

  Scale: ▓▓▓▓▓ Negative         Neutral         █████ Positive

  Turn   Score   Sentiment Bar          Label              Message
  ────── ─────── ────────────────────── ────────────────── ────────────────────────────
  Turn 1  -0.50  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  SOMEWHAT NEGATIVE  "problems with my internet..."
  Turn 3  -1.00  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  NEGATIVE           "terrible...switching providers"
  Turn 5  -0.50  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  SOMEWHAT NEGATIVE  "affecting my job"
  Turn 7  -0.25  ▓▓▓▓▓░░░░░░░░░░░░░░░  MIXED              "should get a credit"
  Turn 9  +1.00  ░░░░░░░░░░██████████  POSITIVE           "appreciate you...thank you"

╔══════════════════════════════════════════════════════════════════════════════╗
║  FULL TURN-BY-TURN DETAIL (All Speakers)                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

  Turn  Speaker   Score   Sentiment Bar          Message
  ───── ──────── ─────── ────────────────────── ───────────────────────────────────
  1     CUSTOMER  -0.50  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  "problems with my internet..."
  2     AGENT     +0.30  ░░░░░░░░░░███░░░░░░░░  "sorry to hear...happy to help"
  3     CUSTOMER  -1.00  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  "terrible...switching providers"
  4     AGENT     +0.20  ░░░░░░░░░░██░░░░░░░░░  "understand your frustration..."
  5     CUSTOMER  -0.50  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  "affecting my job"
  6     AGENT     +0.30  ░░░░░░░░░░███░░░░░░░░  "schedule a technician..."
  7     CUSTOMER  -0.25  ▓▓▓▓▓░░░░░░░░░░░░░░░  "should get a credit"
  8     AGENT     +0.40  ░░░░░░░░░░████░░░░░░░  "applied a 5-day credit..."
  9     CUSTOMER  +1.00  ░░░░░░░░░░██████████  "appreciate you...thank you"
  10    AGENT     +0.60  ░░░░░░░░░░██████░░░░░  "You're welcome!"

╔══════════════════════════════════════════════════════════════════╗
║  CUSTOMER SENTIMENT SUMMARY                                     ║
╚══════════════════════════════════════════════════════════════════╝

  Opening sentiment:  -0.5
  Lowest point:       -1
  Highest point:      1
  Closing sentiment:  1
  Overall shift:      1.5

  *** SUCCESSFUL RESOLUTION ***

╔══════════════════════════════════════════════════════════════════╗
║  ENTITY EXTRACTION                                              ║
╚══════════════════════════════════════════════════════════════════╝

  Entity: Premium 500 Mbps plan (type=CONSUMER_GOOD)
  Entity: $89 (type=PRICE)
  Entity: 7829456 (type=NUMBER)

╔══════════════════════════════════════════════════════════════════╗
║  COMPLETE                                                       ║
╚══════════════════════════════════════════════════════════════════╝

  Full results saved to: results_method2.json
```

---

### M2 — Step 4: Explore the Saved Results

The script saves the full JSON response to `results_method2.json`. Explore it:

```bash
# See the transcript with sentiment per turn:
cat results_method2.json | jq '.transcript.transcriptSegments[] | {text, channelTag, sentiment}'

# See all sentiment annotations:
cat results_method2.json | jq '.latestAnalysis.analysisResult.callAnalysisMetadata.annotations[] | select(.sentimentData != null)'

# See all metadata:
cat results_method2.json | jq '.latestAnalysis.analysisResult.callAnalysisMetadata'
```

**Method 2 is done.** You ran the full pipeline from the terminal using curl.

---

## METHOD 3: Python Client Library

**Time:** 5 minutes
**What this does:** Runs the same pipeline using Python with the official Google Cloud client library. Displays results in nicely formatted tables.

---

### M3 — Step 1: Activate the Virtual Environment

```bash
source venv/bin/activate
```

> If this fails with "No such file or directory", the virtual environment was not created during setup. Create it now:
> ```bash
> python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
> ```

---

### M3 — Step 2: Authenticate for Python

```bash
gcloud auth application-default login
```

This opens a browser window. Click **Allow** to grant access. If you are in Cloud Shell, follow the on-screen instructions (it will give you a URL to open).

---

### M3 — Step 3: Edit the Script

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method3_python_client.py
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method3_python_client.py
```

**Concrete example:**

```bash
sed -i 's/your-project-id/ccai-insights-demo-438291/g' method3_python_client.py
sed -i 's/your-bucket-name/my-ccai-bucket-73921/g' method3_python_client.py
```

---

### M3 — Step 4: Run It

```bash
python method3_python_client.py
```

The script will:
1. Upload `sample_conversation.json` to GCS (if not already there)
2. Create a conversation in CX Insights
3. Run analysis with all annotators
4. Wait for completion
5. Print formatted tables with results

---

### M3 — Step 5: View the Output

The script now produces a rich visual display. The **hero section** is the Customer Sentiment Journey:

```
╔════════════════════════════════════════════════════════════════════════╗
║  CUSTOMER SENTIMENT JOURNEY                                          ║
╚════════════════════════════════════════════════════════════════════════╝

  Scale: ▓▓▓▓▓ Negative    Neutral    █████ Positive

  Turn     Score   ────────────────────  Message
  ──────── ──────  ────────────────────  ───────────────────────────────────────────────
  Turn 1   -0.50   ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  "problems with my internet...frustrating"
           ↘ -0.50
  Turn 3   -1.00   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  "terrible...considering switching providers"
           ↗ +0.50
  Turn 5   -0.50   ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  "affecting my job"
           ↗ +0.25
  Turn 7   -0.25   ▓▓▓▓▓░░░░░░░░░░░░░░░  "should get a credit"
           ↗ +1.25
  Turn 9   +1.00   ░░░░░░░░░░██████████  "appreciate you...thank you"

  ┌──────────────────────────────────────────────────────────────┐
  │  CUSTOMER SENTIMENT SUMMARY                                  │
  ├──────────────────────────────────────────────────────────────┤
  │  Opening sentiment:  -0.50  (SOMEWHAT NEGATIVE)              │
  │  Lowest point:       -1.00  (NEGATIVE          )             │
  │  Highest point:      +1.00  (POSITIVE          )             │
  │  Closing sentiment:  +1.00  (POSITIVE          )             │
  ├──────────────────────────────────────────────────────────────┤
  │  Verdict: SUCCESSFUL RESOLUTION (Sentiment improved by +1.50)│
  └──────────────────────────────────────────────────────────────┘
```

Then a **full detail table** for all speakers, plus entity extraction, intent detection, and issue/topic results.

---

### M3 — Step 6: Try Additional Options

```bash
# Run ONLY sentiment analysis (faster — skips entities, intents, etc.):
python method3_python_client.py --sentiment-only

# Run ALL features (same as default, explicit):
python method3_python_client.py --all-features

# List all conversations in your project:
python method3_python_client.py --list

# Re-analyze a specific conversation by ID:
python method3_python_client.py --analyze CONVERSATION_ID_HERE

# Bulk analyze ALL conversations:
python method3_python_client.py --bulk
```

**Method 3 is done.** You ran the pipeline in Python with formatted output.

---

## METHOD 4: DevKit (Advanced — Audio & Format Conversion)

**Time:** 5-10 minutes
**What this does:** The CX Insights DevKit is a higher-level library for audio transcription, role recognition, and format conversion. This method demonstrates using it for chat transcripts (and shows the audio workflow for reference).

> **Note:** The DevKit is a separate library that may need to be installed from Google's repository. If it is not available, the script automatically falls back to the standard Python client library (Method 3 style).

---

### M4 — Step 1: Edit the Script

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method4_devkit.py
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method4_devkit.py
```

**Concrete example:**

```bash
sed -i 's/your-project-id/ccai-insights-demo-438291/g' method4_devkit.py
sed -i 's/your-bucket-name/my-ccai-bucket-73921/g' method4_devkit.py
```

---

### M4 — Step 2: Run the Chat Workflow

```bash
source venv/bin/activate
python method4_devkit.py --workflow chat
```

This uploads and analyzes the sample chat transcript.

If the DevKit is not installed, the script will print:

```
DevKit not available. Using standard client library as fallback.
```

And will run a complete analysis pipeline using the standard library instead (same as Method 3).

---

### M4 — Step 3: (Optional) Run the Audio Workflow

If you have audio files to transcribe:

```bash
python method4_devkit.py --workflow audio
```

This workflow:
1. Transcribes the audio using Google Speech-to-Text
2. Identifies speaker roles (agent vs. customer)
3. Converts to CX Insights format
4. Uploads and analyzes

> **Note:** You need actual audio files for this. The script provides placeholder instructions for where to put your files.

---

### M4 — Step 4: (Optional) See Format Conversion Examples

```bash
python method4_devkit.py --workflow convert
```

This shows how to convert transcripts from other platforms (Genesys Cloud, AWS Connect) into the CX Insights format.

**Method 4 is done.** You used the DevKit (or its fallback) to analyze conversations.

---

## METHOD 5: BigQuery SQL (Dashboards & Reporting)

**Time:** 10 minutes
**What this does:** Exports all your analyzed conversations to BigQuery (Google's data warehouse), then runs SQL queries for turn-by-turn sentiment analysis at scale.

> **Prerequisite:** You must have at least one analyzed conversation in CX Insights. If you ran Methods 1-4 above, you already have several.

---

### M5 — Step 1: Edit the Export Script

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method5_bigquery_export.sh
```

**Concrete example:**

```bash
sed -i 's/your-project-id/ccai-insights-demo-438291/g' method5_bigquery_export.sh
```

---

### M5 — Step 2: Run the Export

```bash
chmod +x method5_bigquery_export.sh
./method5_bigquery_export.sh
```

The script will:

1. **Create** a BigQuery dataset called `ccai_insights_data`
2. **Export** all conversations from CX Insights to BigQuery
3. **Verify** the export by counting rows and running a quick sentiment summary

**Expected output:**

```
============================================================
  CCAI Insights: Method 5 — BigQuery Export Setup
============================================================

  Step 1/3: Creating BigQuery dataset
  Creating dataset: ccai-insights-demo-438291:ccai_insights_data
  Dataset created.

  Step 2/3: Exporting conversations to BigQuery
  Destination: ccai-insights-demo-438291.ccai_insights_data.conversations
  Export is a long-running operation.
  Polling for completion...
  Export complete!

  Step 3/3: Verifying export
  Rows exported: 4

============================================================
  EXPORT COMPLETE
============================================================
```

---

### M5 — Step 3: Open BigQuery Console

Open this URL in your browser:

```
https://console.cloud.google.com/bigquery
```

Or click the link that the script printed at the end.

---

### M5 — Step 4: Run SQL Queries

Open the file `method5_bigquery_queries.sql`. It contains 10 ready-to-use queries. Here are the most important ones to try:

**Query 1: Turn-by-Turn Sentiment for All Conversations**

Copy this into the BigQuery query editor and click **Run**:

```sql
SELECT
    conversationName,
    s.speakerTag AS speaker_id,
    CASE
        WHEN s.speakerTag = 1 THEN 'CUSTOMER'
        WHEN s.speakerTag = 2 THEN 'AGENT'
        ELSE 'UNKNOWN'
    END AS speaker_role,
    s.text AS turn_text,
    s.sentimentScore AS sentiment_score,
    s.sentimentMagnitude AS sentiment_magnitude,
    CASE
        WHEN s.sentimentScore >= 0.75 THEN 'POSITIVE'
        WHEN s.sentimentScore >= 0.25 THEN 'SOMEWHAT_POSITIVE'
        WHEN s.sentimentScore >= -0.25 AND s.sentimentMagnitude > 0.5 THEN 'MIXED'
        WHEN s.sentimentScore >= -0.25 THEN 'NEUTRAL'
        WHEN s.sentimentScore >= -0.75 THEN 'SOMEWHAT_NEGATIVE'
        ELSE 'NEGATIVE'
    END AS sentiment_label
FROM
    `YOUR_PROJECT_ID.ccai_insights_data.conversations`,
    UNNEST(sentences) AS s
ORDER BY
    conversationName,
    s.createTime;
```

> **Important:** Replace `YOUR_PROJECT_ID` with your actual project ID (e.g., `ccai-insights-demo-438291`).

**Query 3: Conversation Sentiment Summary**

```sql
SELECT
    conversationName,
    COUNT(*) AS total_turns,
    ROUND(AVG(s.sentimentScore), 3) AS avg_sentiment,
    ROUND(MIN(s.sentimentScore), 3) AS worst_moment,
    ROUND(MAX(s.sentimentScore), 3) AS best_moment,
    ROUND(MAX(s.sentimentScore) - MIN(s.sentimentScore), 3) AS sentiment_range
FROM
    `YOUR_PROJECT_ID.ccai_insights_data.conversations`,
    UNNEST(sentences) AS s
GROUP BY
    conversationName
ORDER BY
    avg_sentiment ASC;
```

**Query 5: Detect Negative-to-Positive Shifts**

```sql
SELECT
    conversationName,
    ROUND(MIN(s.sentimentScore), 3) AS lowest_point,
    ROUND(MAX(s.sentimentScore), 3) AS highest_point,
    ROUND(MAX(s.sentimentScore) - MIN(s.sentimentScore), 3) AS recovery_score,
    CASE
        WHEN MIN(s.sentimentScore) < -0.3 AND MAX(s.sentimentScore) > 0.3
        THEN 'YES - Successful Recovery'
        ELSE 'No significant shift'
    END AS sentiment_recovery
FROM
    `YOUR_PROJECT_ID.ccai_insights_data.conversations`,
    UNNEST(sentences) AS s
GROUP BY
    conversationName
HAVING
    MIN(s.sentimentScore) < -0.3 AND MAX(s.sentimentScore) > 0.3
ORDER BY
    recovery_score DESC;
```

> The file `method5_bigquery_queries.sql` contains 7 more queries (10 total). Open it and try them all.

**Method 5 is done.** You exported data to BigQuery and ran SQL sentiment queries.

---

## PHASE 3: UNDERSTANDING YOUR RESULTS

---

### How Sentiment Scores Work

Every message gets a **score** between -1.0 and +1.0:

```
-1.0                    0.0                    +1.0
  |─────────────────────|─────────────────────|
  Very Negative      Neutral            Very Positive
  "This is terrible"  "Okay"          "Thank you so much!"
```

And a **magnitude** from 0.0 upward that measures emotional intensity:

| Score | Magnitude | Meaning |
|-------|-----------|---------|
| -0.8  | 0.9       | Strongly negative ("this is awful") |
| -0.3  | 0.3       | Mildly negative ("not great") |
|  0.0  | 0.0       | Neutral ("okay") |
|  0.0  | 0.8       | Mixed ("it's good but also bad") |
|  0.3  | 0.3       | Mildly positive ("that's nice") |
|  0.8  | 0.9       | Strongly positive ("this is amazing!") |

### Sentiment Labels

| Score Range       | Label              |
|-------------------|--------------------|
| 0.75 to 1.0       | Positive           |
| 0.25 to 0.74      | Somewhat Positive  |
| -0.25 to 0.24     | Neutral (or Mixed if high magnitude) |
| -0.74 to -0.26    | Somewhat Negative  |
| -1.0 to -0.75     | Negative           |

### Conversation-Level vs. Turn-Level

- **Turn-level:** Each individual message gets its own score. This is the "turn-by-turn" analysis.
- **Conversation-level:** The entire conversation gets an aggregated score per channel (customer channel, agent channel).

### What Gets Scored

CX Insights primarily scores **customer** turns for sentiment. Agent turns appear in the transcript but typically receive neutral or mildly positive scores since they are expected to be professional.

### Why Turn-by-Turn Matters

Turn-by-turn shows the **emotional journey** of a conversation:

```
Turn 1:  -0.50  Customer calls in frustrated
Turn 3:  -1.00  Gets more upset (threatens to leave)
Turn 5:  -0.50  Still negative but calmer
Turn 7:  -0.25  Agent offers solution, customer slightly hopeful
Turn 9:  +1.00  Issue resolved, customer is happy
```

This tells you the agent **successfully de-escalated** and resolved the issue. You can use this pattern across thousands of conversations to find:
- Which agents are best at turning negative calls positive
- Where customers tend to get most frustrated
- Whether your resolution process actually makes customers happy
- Which issue types have the worst sentiment

---

## QUICK REFERENCE: ALL COMMANDS IN ONE PLACE

Here is every command from this guide, in order, for easy copy-pasting.

### Setup (run once)

```bash
# Navigate to the project
cd ~/ccai-sentiment-analysis

# Edit setup script (replace with YOUR values)
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' 00_setup.sh
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' 00_setup.sh

# Run setup
chmod +x 00_setup.sh
./00_setup.sh
# (type "y" when asked about Python dependencies)
```

### Method 2: curl

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method2_curl_pipeline.sh
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method2_curl_pipeline.sh
chmod +x method2_curl_pipeline.sh
./method2_curl_pipeline.sh
```

### Method 3: Python

```bash
source venv/bin/activate
gcloud auth application-default login
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method3_python_client.py
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method3_python_client.py
python method3_python_client.py
```

### Method 4: DevKit

```bash
source venv/bin/activate
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method4_devkit.py
sed -i 's/your-bucket-name/YOUR_BUCKET_NAME/g' method4_devkit.py
python method4_devkit.py --workflow chat
```

### Method 5: BigQuery

```bash
sed -i 's/your-project-id/YOUR_PROJECT_ID/g' method5_bigquery_export.sh
chmod +x method5_bigquery_export.sh
./method5_bigquery_export.sh
# Then open https://console.cloud.google.com/bigquery
# Copy queries from method5_bigquery_queries.sql and run them
```

---

## TROUBLESHOOTING

### "ERROR: You must edit this script and set your PROJECT_ID first"

You forgot to run the `sed` command. Go back and replace the placeholder values.

### "ERROR 403: The caller does not have permission"

Run this in Cloud Shell:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/contactcenterinsights.editor"
```

### "ERROR 403: billing not enabled"

Go to https://console.cloud.google.com/billing and link billing to your project.

### "Bucket name already exists"

Bucket names are globally unique across all of Google Cloud. Add more random numbers:

```bash
# Instead of: my-ccai-bucket
# Try:        my-ccai-bucket-82947
```

### "ModuleNotFoundError: No module named 'google.cloud'"

The Python virtual environment is not activated. Run:

```bash
source venv/bin/activate
```

If the venv does not exist:

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### "Analysis is taking a long time"

Analysis typically takes 1-2 minutes. Methods 2 and 3 poll automatically. For Method 1 (Console), refresh the page after 2 minutes.

### "No sentiment results appear"

Make sure you waited for the analysis to complete. In Method 1, click **Analyze** and wait. In Methods 2/3, the script polls and tells you when it is done.

### "jq: command not found"

Install jq (needed for Method 2):

```bash
# Cloud Shell: already installed
# Ubuntu/Debian:
sudo apt-get install jq
# macOS:
brew install jq
```

---

## WHAT TO DO NEXT

Now that you have run all 5 methods:

1. **Edit the sample conversation** — Modify `sample_conversation.json` with your own text and re-run any method
2. **Import real data** — Replace the sample with actual customer support transcripts
3. **Build dashboards** — Use the BigQuery queries as a foundation for Looker or Data Studio dashboards
4. **Set up continuous export** — Configure CX Insights to automatically export new conversations to BigQuery
5. **Read the full reference** — See [README.md](./README.md) for the complete API reference, annotator options, and pricing
6. **Check the official docs** — https://docs.cloud.google.com/contact-center/insights/docs

---

## FILE REFERENCE

| File | What It Is |
|------|-----------|
| `STEP_BY_STEP_GUIDE.md` | This document — complete walkthrough |
| `GETTING_STARTED.md` | Beginner intro with glossary and background |
| `README.md` | Full reference guide with API details |
| `00_setup.sh` | One-time setup script |
| `sample_conversation.json` | 10-turn ISP support chat (sample data) |
| `method1_console_walkthrough.md` | Detailed console UI walkthrough |
| `method2_curl_pipeline.sh` | curl/REST API pipeline |
| `method3_python_client.py` | Python client library pipeline |
| `method4_devkit.py` | DevKit / advanced pipeline |
| `method5_bigquery_export.sh` | BigQuery export script |
| `method5_bigquery_queries.sql` | 10 SQL queries for BigQuery |
| `requirements.txt` | Python package dependencies |
