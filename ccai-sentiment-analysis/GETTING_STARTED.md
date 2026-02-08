# Getting Started: Your First Sentiment Analysis in 20 Minutes

## Read This First

This guide assumes **you have never used Google Cloud before**. It will walk you through every single step, from creating an account to seeing turn-by-turn sentiment scores on a real conversation. Nothing is skipped.

If you already have Google Cloud experience, jump straight to the [README.md](./README.md) instead.

---

## What You Will Build

You will take this sample customer support conversation:

```
CUSTOMER: "I've been having problems with my internet... it's really frustrating."
AGENT:    "I'm sorry to hear that. I'd be happy to help."
CUSTOMER: "The service has been terrible. I'm considering switching providers."
AGENT:    "I understand your frustration. Let me check the network status..."
CUSTOMER: "I work from home and the disconnections are affecting my job."
AGENT:    "I'd like to schedule a technician visit. Would tomorrow work?"
CUSTOMER: "What about the three days I've already lost? I should get a credit."
AGENT:    "I've applied a 5-day service credit to your account."
CUSTOMER: "I appreciate you taking care of that. Thank you for your help."
AGENT:    "You're welcome! The technician is booked for tomorrow."
```

...and feed it into Google's AI, which will return scores like this for each customer message:

```
Turn 1: "really frustrating"              -->  Score: -0.50  (Somewhat Negative)
Turn 3: "terrible...considering switching" -->  Score: -1.00  (Negative)
Turn 5: "affecting my job"                 -->  Score: -0.50  (Somewhat Negative)
Turn 7: "should get a credit"              -->  Score: -0.25  (Mixed)
Turn 9: "appreciate you...thank you"       -->  Score: +1.00  (Positive)
```

The AI tracks the customer's **emotional journey** from frustrated to satisfied.

---

## What You Will Need

- A web browser (Chrome, Firefox, Safari, Edge)
- A Google account (Gmail works)
- A credit card (Google Cloud has a free trial, but requires a card on file)

That's it. All the tools run in your browser.

---

## Part 1: Create Your Google Cloud Account (5 minutes)

> **Already have a Google Cloud account?** Skip to [Part 2](#part-2-create-a-project-2-minutes).

### Step 1.1: Go to Google Cloud

Open your browser and go to:

```
https://cloud.google.com
```

### Step 1.2: Click "Get started for free"

You will see a blue button that says **"Get started for free"** or **"Start free"**. Click it.

### Step 1.3: Sign in with your Google account

Use any Gmail or Google Workspace account. If you don't have one, create one.

### Step 1.4: Set up billing

Google Cloud requires a credit card, but gives you **$300 in free credits** for 90 days. Enter your billing information. You will NOT be charged during the free trial unless you manually upgrade.

### Step 1.5: Accept the terms of service

Check the boxes and click **Continue** or **Start my free trial**.

You are now in the **Google Cloud Console** — the main dashboard for everything.

---

## Part 2: Create a Project (2 minutes)

Everything in Google Cloud lives inside a **project**. Think of it as a folder that holds all your work.

### Step 2.1: Open the project selector

At the very top of the Google Cloud Console, you will see a dropdown that says something like **"My First Project"** or **"Select a project"**. Click on it.

### Step 2.2: Create a new project

1. In the popup, click **New Project** (upper-right corner)
2. **Project name**: Type `ccai-insights-demo` (or anything you like)
3. **Organization**: Leave as default (or "No organization")
4. Click **Create**
5. Wait 10-20 seconds for it to be created

### Step 2.3: Find your Project ID

This is the single most important value. You will use it everywhere.

1. Click the project dropdown at the top again
2. You will see your project listed with TWO names:
   - **Project name**: What you typed (e.g., `ccai-insights-demo`)
   - **Project ID**: An auto-generated unique string (e.g., `ccai-insights-demo-438291`)
3. **Copy the Project ID** (NOT the project name). Write it down somewhere.

> **Example**: If your Project ID is `ccai-insights-demo-438291`, that's the value you will paste into scripts later.

### Step 2.4: Select your project

Make sure your new project is selected in the top dropdown. The dropdown text should show your project name.

---

## Part 3: Open Cloud Shell (1 minute)

**Cloud Shell** is a free terminal that runs in your browser. It already has all the tools you need installed (`gcloud`, `jq`, `python3`). No local installation required.

### Step 3.1: Activate Cloud Shell

1. Look at the top-right of the Google Cloud Console
2. Find the icon that looks like a terminal/command prompt: `>_`
3. Click it
4. A black terminal panel will appear at the bottom of your screen
5. Wait for it to say something like `yourname@cloudshell:~$` — that means it's ready

> **What is this?** Cloud Shell is a small Linux computer that Google gives you for free. You type commands into it and it runs them. All the tools we need are already installed.

### Step 3.2: Confirm it works

Type this in Cloud Shell and press Enter:

```bash
echo "Cloud Shell is working!"
```

You should see `Cloud Shell is working!` printed back. If so, you're ready.

---

## Part 4: Download This Project (1 minute)

You need to get the scripts and sample data onto your Cloud Shell machine.

### Step 4.1: Upload the files

**Option A: Clone from git (if this is in a repository):**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/ccai-sentiment-analysis
```

**Option B: Upload manually:**

1. In Cloud Shell, click the three-dot menu (**...**) at the top of the terminal
2. Click **Upload**
3. Select all the files from the `ccai-sentiment-analysis/` folder on your computer
4. They will upload to your Cloud Shell home directory

Then navigate to them:

```bash
cd ~/ccai-sentiment-analysis
```

### Step 4.2: Verify the files are there

```bash
ls -la
```

You should see:

```
00_setup.sh
GETTING_STARTED.md
README.md
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

## Part 5: Run the Setup Script (3 minutes)

This one script enables all the APIs, creates your storage bucket, and uploads the sample data.

### Step 5.1: Edit the script with your Project ID

You need to put YOUR Project ID into the script. Here's how:

```bash
# Open the file in the built-in editor
# Replace my-project-id-12345 with YOUR actual Project ID from Part 2
sed -i 's/your-project-id/my-project-id-12345/g' 00_setup.sh

# Also set your bucket name (must be globally unique, so add random numbers)
sed -i 's/your-bucket-name/my-ccai-bucket-12345/g' 00_setup.sh
```

> **What's a bucket?** A Cloud Storage bucket is like a folder in Google's cloud where you store files. The name must be unique across ALL of Google Cloud, so add some random numbers to make it unique (e.g., `my-ccai-bucket-73921`).

**Alternatively, edit the file manually:**

```bash
# Open in the Cloud Shell editor
cloudshell edit 00_setup.sh
```

This opens a text editor in your browser. Change these two lines near the top:
- `PROJECT_ID="your-project-id"` --> `PROJECT_ID="my-project-id-12345"`
- `BUCKET_NAME="your-bucket-name"` --> `BUCKET_NAME="my-ccai-bucket-12345"`

Save the file (Ctrl+S or Cmd+S).

### Step 5.2: Run the setup

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

  Step 2/6: Setting project to my-project-id-12345
  Project set to: my-project-id-12345

  Step 3/6: Enabling required APIs (this may take a minute)
  Enabling Contact Center AI Insights API...
  Enabling Cloud Storage API...
  ...

  Step 4/6: Creating Cloud Storage bucket
  Creating bucket gs://my-ccai-bucket-12345...

  Step 5/6: Uploading sample conversation to Cloud Storage
  Uploading sample_conversation.json...

  Step 6/6: Python dependencies (optional)
  Install Python dependencies now? (y/n):
```

Type `y` and press Enter if you plan to use Methods 3/4/5. Type `n` if you just want Methods 1 or 2.

### Step 5.3: Confirm success

At the end you should see:

```
============================================================
  SETUP COMPLETE
============================================================

  Project:     my-project-id-12345
  Bucket:      gs://my-ccai-bucket-12345
  Transcript:  gs://my-ccai-bucket-12345/transcripts/sample_conversation.json
```

**Write down these three values.** You will need them in every method.

> **Something went wrong?** The most common error is `ERROR 403: billing not enabled`. Go to https://console.cloud.google.com/billing and make sure billing is linked to your project.

---

## Part 6: Pick Your Method and Go

You are now fully set up. Pick ONE method to try first:

---

### Path A: "I just want to see it work" --> Method 1 (Console, No Code)

Open [`method1_console_walkthrough.md`](./method1_console_walkthrough.md) and follow the steps. Everything is done in your browser with clicks.

**Quick version:**
1. Go to https://console.cloud.google.com/contact-center/insights
2. Click **Conversation Hub** > **Import** > **Chat** > **File**
3. Paste: `gs://my-ccai-bucket-12345/transcripts/sample_conversation.json`
4. Set Agent ID to `agent-001`, click **Import**
5. Click the conversation > click **Analyze**
6. Wait 1-2 minutes, then scroll to **Conversation spotlight** to see the sentiment chart

---

### Path B: "I want to run it from the terminal" --> Method 2 (curl)

This runs entirely in Cloud Shell. No Python needed.

```bash
# Step 1: Edit the script with your values
sed -i 's/your-project-id/my-project-id-12345/g' method2_curl_pipeline.sh
sed -i 's/your-bucket-name/my-ccai-bucket-12345/g' method2_curl_pipeline.sh

# Step 2: Run it
chmod +x method2_curl_pipeline.sh
./method2_curl_pipeline.sh
```

The script will upload the conversation, analyze it, wait for results, and then print:
- Conversation-level sentiment scores
- Turn-by-turn sentiment for each message
- Entities extracted (products, dates, amounts)
- Detected intents and issues

Results are saved to `results_method2.json`.

---

### Path C: "I want Python code I can customize" --> Method 3 (Python)

```bash
# Step 1: Activate the virtual environment (created during setup)
source venv/bin/activate

# Step 2: Edit the script with your values
sed -i 's/your-project-id/my-project-id-12345/g' method3_python_client.py
sed -i 's/your-bucket-name/my-ccai-bucket-12345/g' method3_python_client.py

# Step 3: Authenticate for Python
gcloud auth application-default login

# Step 4: Run it
python method3_python_client.py
```

The script will print formatted tables showing turn-by-turn sentiment, entities, intents, and more.

**Other things you can do with the Python script:**

```bash
# Only run sentiment analysis (faster):
python method3_python_client.py --sentiment-only

# List all your conversations:
python method3_python_client.py --list

# Re-analyze a specific conversation:
python method3_python_client.py --analyze CONVERSATION_ID

# Bulk analyze every conversation:
python method3_python_client.py --bulk
```

---

### Path D: "I have audio files, not text" --> Method 4 (DevKit)

```bash
# Step 1: Edit the script
sed -i 's/your-project-id/my-project-id-12345/g' method4_devkit.py
sed -i 's/your-bucket-name/my-ccai-bucket-12345/g' method4_devkit.py

# Step 2: Run the chat workflow (uses our sample text file)
source venv/bin/activate
python method4_devkit.py --workflow chat

# Step 3: (If you have audio files) Run the audio workflow
python method4_devkit.py --workflow audio
```

---

### Path E: "I want SQL queries for dashboards" --> Method 5 (BigQuery)

This requires at least one analyzed conversation (do Path A, B, or C first).

```bash
# Step 1: Edit the export script
sed -i 's/your-project-id/my-project-id-12345/g' method5_bigquery_export.sh

# Step 2: Export data to BigQuery
chmod +x method5_bigquery_export.sh
./method5_bigquery_export.sh

# Step 3: Open BigQuery in your browser
# https://console.cloud.google.com/bigquery

# Step 4: Copy a query from method5_bigquery_queries.sql,
#          replace YOUR_PROJECT_ID and YOUR_DATASET, and run it
```

---

## Part 7: Understanding What You See

### What is a Sentiment Score?

Every customer message gets a number between **-1.0** and **+1.0**:

```
-1.0                    0.0                    +1.0
  |─────────────────────|─────────────────────|
  Very Negative      Neutral            Very Positive
  "This is terrible"  "Okay"          "Thank you so much!"
```

### What is Magnitude?

Magnitude measures how **strongly** someone feels, regardless of positive or negative:

- Score = 0.0, Magnitude = 0.0 --> Neutral ("okay")
- Score = 0.0, Magnitude = 0.8 --> Mixed ("it's good but also bad")
- Score = -0.8, Magnitude = 0.9 --> Strongly negative ("this is awful")
- Score = 0.8, Magnitude = 0.9 --> Strongly positive ("this is amazing!")

### What does the AI score?

CX Insights primarily scores **customer** turns. Agent turns appear in the transcript but don't get individual sentiment scores (they do get a conversation-level score).

### Why does this matter?

Turn-by-turn sentiment shows you the **emotional journey** of a conversation:

```
Turn 1:  -0.50  Customer calls in frustrated
Turn 3:  -1.00  Customer gets more upset (threatens to leave)
Turn 5:  -0.50  Still negative but slightly calmer
Turn 7:  -0.25  Agent offers solution, customer slightly hopeful
Turn 9:  +1.00  Agent resolves issue, customer is happy

This tells you: The agent successfully de-escalated and resolved the issue.
```

This is valuable because you can find:
- Which agents are best at turning negative calls positive
- Where in a conversation customers tend to get most frustrated
- Whether your resolution process actually makes customers happy
- Which types of issues have the worst customer sentiment

---

## Glossary: Terms You Will See

| Term | What It Means |
|------|--------------|
| **GCP** | Google Cloud Platform — the cloud computing service |
| **Project** | A container for all your Google Cloud resources |
| **Project ID** | A unique identifier for your project (e.g., `my-project-438291`) |
| **Bucket** | A container for storing files in Google Cloud Storage |
| **GCS** | Google Cloud Storage — where you put files |
| **API** | Application Programming Interface — a way to talk to Google's services programmatically |
| **gcloud** | Google's command-line tool for managing cloud resources |
| **Cloud Shell** | A free browser-based terminal provided by Google Cloud |
| **CX Insights** | Customer Experience Insights — the product we're using |
| **CCAI** | Contact Center AI — the broader Google product family |
| **Transcript** | A text record of a conversation |
| **Annotator** | An AI model that analyzes one aspect of a conversation |
| **Sentiment** | The emotional tone of a message (positive, negative, neutral) |
| **Magnitude** | How strong the emotion is, regardless of positive/negative |
| **Long-running operation** | A task that takes time; you start it and check back later |
| **curl** | A command-line tool for making HTTP requests |
| **jq** | A command-line tool for parsing JSON |
| **REST API** | A way to interact with a service by sending HTTP requests |
| **BigQuery** | Google's data warehouse for running SQL queries on large datasets |

---

## Common Problems and Fixes

### "I can't find my Project ID"

1. Go to https://console.cloud.google.com
2. Click the project dropdown at the top
3. Your Project ID is the grey text under the project name (it often has numbers at the end)

### "ERROR 403: The caller does not have permission"

Your account needs the right permissions. Run this in Cloud Shell:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/contactcenterinsights.editor"
```

### "ERROR: Billing account not found"

1. Go to https://console.cloud.google.com/billing
2. Create a billing account if you don't have one
3. Link it to your project

### "Bucket name already exists"

Bucket names are globally unique. Add random numbers:

```bash
# Instead of: my-ccai-bucket
# Try:        my-ccai-bucket-82947
```

### "The setup script says 'your-project-id'"

You forgot to edit the script. The placeholder values must be replaced with your real values. See [Part 5](#part-5-run-the-setup-script-3-minutes).

### "I don't see any sentiment results after analysis"

Analysis takes 1-2 minutes. If you are using Method 1 (Console), refresh the page. If using Method 2 or 3, the script polls automatically.

---

## Next Steps After Your First Analysis

Once you've completed your first analysis, here are ideas for what to do next:

1. **Modify the sample conversation** - Edit `sample_conversation.json` to test with your own text
2. **Try a different method** - If you did Method 1, try Method 2 or 3
3. **Import your own data** - Replace the sample with a real conversation transcript
4. **Set up BigQuery** - Export your data and build dashboards (Method 5)
5. **Read the full reference** - See [README.md](./README.md) for the complete API reference
6. **Check the official docs** - https://docs.cloud.google.com/contact-center/insights/docs
