# Method 1: Google Cloud Console (No Code Required)

## Estimated Time: 10-15 minutes

This is the easiest way to get started. You do everything in your browser. No code, no terminal, no scripting.

---

## Prerequisites Checklist

Before you begin, make sure you have completed `00_setup.sh`, or at minimum:

- [ ] A Google Cloud project with billing enabled
- [ ] The Contact Center AI Insights API is enabled
- [ ] The Cloud Storage API is enabled
- [ ] A Cloud Storage bucket with your transcript file uploaded
- [ ] `sample_conversation.json` uploaded to `gs://YOUR_BUCKET_NAME/transcripts/`

---

## Step 1: Open the CX Insights Console

1. Open your browser and go to:

   ```
   https://console.cloud.google.com/contact-center/insights
   ```

   **Alternative URL** (direct CX Insights console):
   ```
   https://ccai.cloud.google.com/insights/projects
   ```

2. If prompted, select your **Google Cloud project** from the dropdown at the top of the page.

3. You should now see the CX Insights landing page with a left sidebar navigation.

> **First time?** If this is your first visit, the console may ask you to enable the API or accept terms of service. Follow the on-screen prompts.

---

## Step 2: Navigate to the Conversation Hub

1. In the left sidebar, click **Conversation Hub**
2. This is where all imported conversations live
3. If this is a brand new project, the list will be empty

---

## Step 3: Import Your Sample Conversation

1. Click the **Import** button (top of the Conversation Hub page)

2. You will see an import wizard. Select the conversation type:
   - Click **Chat** (since our sample data is a text transcript)

3. Click **Next**

4. On the next screen, select **File** (we are importing a single file)

5. In the **Transcript URI** field, enter the path to your uploaded file:
   ```
   gs://YOUR_BUCKET_NAME/transcripts/sample_conversation.json
   ```
   Replace `YOUR_BUCKET_NAME` with your actual bucket name.

6. Click **Next**

7. On the metadata screen:
   - **Agent ID**: Enter `agent-001` (or any identifier you want)
   - **Agent display name**: Enter `Support Agent` (optional)

8. Click **Import**

9. Wait for the import to complete. You should see a success message. This usually takes 10-30 seconds.

---

## Step 4: Open the Imported Conversation

1. You should now be back on the Conversation Hub page

2. Your newly imported conversation will appear in the list

3. Click on the **conversation name** (or the row) to open it

4. You will see the transcript displayed as a chat view, with each message shown in order:
   - **Customer messages** on one side
   - **Agent messages** on the other side

---

## Step 5: Run the Analysis

1. On the conversation detail page, look for the **Analyze** button (usually at the top)

2. Click **Analyze**

3. The system will run ALL annotators by default:
   - Sentiment analysis
   - Entity extraction
   - Intent detection
   - Issue/topic classification
   - And more

4. Wait for the analysis to complete. This typically takes **1-2 minutes**.

5. The page will refresh automatically when done, or you may need to refresh manually.

---

## Step 6: View Turn-by-Turn Sentiment Results

Once the analysis completes, the conversation page will show rich annotations.

### 6a: Conversation Spotlight

1. Scroll down to the **Conversation spotlight** section

2. Here you will see:
   - A **sentiment timeline** chart showing how sentiment changes across the conversation
   - **Top positive moments** (highlighted in blue)
   - **Top negative moments** (highlighted in red)

3. Each customer turn is annotated with a color indicator:
   - **Blue** = Positive sentiment
   - **Red** = Negative sentiment
   - The intensity of the color indicates the magnitude (strength)

### 6b: Individual Turn Sentiment

1. In the transcript view, each message may show a small sentiment indicator

2. Hover over a customer message to see its specific:
   - **Sentiment score** (-1.0 to 1.0)
   - **Sentiment label** (negative, somewhat_negative, neutral, positive, etc.)

### 6c: Conversation-Level Summary

1. Look at the top of the conversation page for the overall sentiment:
   - **Customer sentiment**: The overall emotional tone of the customer
   - **Agent sentiment**: The overall emotional tone of the agent

### 6d: Information Tab

1. Click the **Information** tab on the conversation detail page

2. This shows:
   - Detailed **sentiment rationale** (why the system assigned specific scores)
   - **Entities** mentioned in the conversation (products, dates, amounts)
   - **Topics/issues** detected
   - **Intent** of the customer

---

## Step 7: Explore Other Features While You Are Here

Since the analysis ran all annotators, explore these additional features:

### Issue/Topic Detection
- Look in the Information tab for **Detected Issues**
- This shows what the conversation is about (e.g., "Internet Service Issue", "Billing Credit")

### Entity Extraction
- Look for **Entities** in the Information tab
- These are specific things mentioned (e.g., "Premium 500 Mbps plan", "$89", "7829456")

### Conversation Summary
- Some conversations will show an auto-generated **summary**
- This is a brief description of what happened in the conversation

---

## Step 8: View Sentiment Across Multiple Conversations (Quality AI)

If you import multiple conversations, you can view aggregate sentiment trends:

1. In the left sidebar, click **Quality AI**
2. Click **Conversations**
3. You'll see a list of conversations with sentiment indicators
4. Click on any conversation to see the detailed spotlight view

### Analytics Dashboard
1. In the left sidebar, click **Explore** or **Analytics**
2. This shows aggregate charts across all your conversations:
   - Sentiment distribution (what percentage positive/negative/neutral)
   - Topic breakdown (top call drivers)
   - Agent performance comparisons

---

## What You Learned

In this method, you:
- Imported a chat transcript through the browser
- Ran ML analysis with one click
- Viewed turn-by-turn sentiment for each customer message
- Explored conversation-level sentiment summaries
- Saw how sentiment shifts from negative to positive as the agent resolves the issue

---

## Expected Results for Our Sample Conversation

Based on the sample conversation, you should see:

| Turn | Speaker  | Text (abbreviated)                                     | Expected Sentiment    |
|------|----------|-------------------------------------------------------|-----------------------|
| 1    | Customer | "problems...really frustrating"                        | Somewhat Negative     |
| 2    | Agent    | "sorry to hear...happy to help"                        | (Agent - not scored)  |
| 3    | Customer | "terrible service...considering switching"              | Negative              |
| 4    | Agent    | "understand your frustration...resolve this"            | (Agent - not scored)  |
| 5    | Customer | "affecting my job"                                      | Somewhat Negative     |
| 6    | Agent    | "schedule a technician"                                 | (Agent - not scored)  |
| 7    | Customer | "should get a credit"                                   | Mixed/Slightly Neg.   |
| 8    | Agent    | "applied a 5-day credit"                                | (Agent - not scored)  |
| 9    | Customer | "appreciate you...thank you"                            | Positive              |
| 10   | Agent    | "You're welcome!"                                       | (Agent - not scored)  |

**Key insight:** The sentiment arc goes from **negative** (frustrated customer) to **positive** (resolved issue + proactive credit). This is the power of turn-by-turn analysis.

---

## Next Steps

- **Want automation?** Try [Method 2 (curl)](./method2_curl_pipeline.sh) or [Method 3 (Python)](./method3_python_client.py)
- **Have many conversations?** Try [Method 5 (BigQuery)](./method5_bigquery_queries.sql) for SQL-based analysis at scale
- **Have audio files?** Try [Method 4 (DevKit)](./method4_devkit.py) for transcription + analysis
