#!/usr/bin/env bash
# ==============================================================================
# Method 5 (Part 1): Set up BigQuery Export
# ==============================================================================
#
# WHAT THIS DOES:
#   Creates a BigQuery dataset, configures CX Insights to export data there,
#   and triggers an initial export. Once done, you can run the SQL queries
#   in method5_bigquery_queries.sql to analyze turn-by-turn sentiment at scale.
#
# HOW TO RUN:
#   1. Complete 00_setup.sh and import + analyze at least one conversation
#      (using Method 1, 2, 3, or 4)
#   2. Edit the 3 variables below
#   3. Run:
#        chmod +x method5_bigquery_export.sh
#        ./method5_bigquery_export.sh
#   4. Open method5_bigquery_queries.sql and run the queries in the
#      BigQuery console
#
# ==============================================================================

set -euo pipefail

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES                                                        ║
# ╚════════════════════════════════════════════════════════════════════════════╝
PROJECT_ID="your-project-id"
LOCATION="us-central1"
BQ_DATASET="ccai_insights_data"    # BigQuery dataset name (will be created)
BQ_TABLE="conversations"           # BigQuery table name

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  DO NOT EDIT BELOW THIS LINE                                              ║
# ╚════════════════════════════════════════════════════════════════════════════╝

BASE_URL="https://contactcenterinsights.googleapis.com/v1"
PARENT="projects/$PROJECT_ID/locations/$LOCATION"

echo ""
echo "============================================================"
echo "  CCAI Insights: Method 5 — BigQuery Export Setup"
echo "============================================================"
echo ""

if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "ERROR: Edit this script and set PROJECT_ID first."
    exit 1
fi


# ==============================================================================
# STEP 1: Create BigQuery dataset
# ==============================================================================
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 1/3: Creating BigQuery dataset"
echo "──────────────────────────────────────────────────────────────"
echo ""

if bq show --dataset "$PROJECT_ID:$BQ_DATASET" &>/dev/null; then
    echo "  Dataset $BQ_DATASET already exists. Skipping."
else
    echo "  Creating dataset: $PROJECT_ID:$BQ_DATASET"
    bq mk --dataset \
        --location="US" \
        --description="CCAI Insights exported conversation data" \
        "$PROJECT_ID:$BQ_DATASET"
    echo "  Dataset created."
fi


# ==============================================================================
# STEP 2: Trigger data export from CX Insights to BigQuery
# ==============================================================================
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 2/3: Exporting conversations to BigQuery"
echo "──────────────────────────────────────────────────────────────"
echo ""
echo "  Destination: $PROJECT_ID.$BQ_DATASET.$BQ_TABLE"
echo ""

EXPORT_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{
        \"bigQueryDestination\": {
            \"projectId\": \"$PROJECT_ID\",
            \"dataset\": \"$BQ_DATASET\",
            \"table\": \"$BQ_TABLE\"
        },
        \"writeDisposition\": \"WRITE_TRUNCATE\"
    }" \
    "$BASE_URL/$PARENT/insightsdata:export")

echo "  Export response:"
echo "$EXPORT_RESPONSE" | jq '.' 2>/dev/null || echo "$EXPORT_RESPONSE"

# Check if it's a long-running operation
OPERATION_NAME=$(echo "$EXPORT_RESPONSE" | jq -r '.name // empty' 2>/dev/null)

if [ -n "$OPERATION_NAME" ]; then
    echo ""
    echo "  Export is a long-running operation."
    echo "  Operation: $OPERATION_NAME"
    echo ""
    echo "  Polling for completion..."

    MAX_ATTEMPTS=60
    ATTEMPT=0
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        ATTEMPT=$((ATTEMPT + 1))
        STATUS=$(curl -s -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "$BASE_URL/$OPERATION_NAME")

        DONE=$(echo "$STATUS" | jq -r '.done // false' 2>/dev/null)
        if [ "$DONE" = "true" ]; then
            echo "  Export complete! (after $ATTEMPT polls)"
            break
        fi
        echo "  Waiting... ($ATTEMPT/$MAX_ATTEMPTS)"
        sleep 5
    done
fi


# ==============================================================================
# STEP 3: Verify the export
# ==============================================================================
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 3/3: Verifying export"
echo "──────────────────────────────────────────────────────────────"
echo ""

echo "  Checking row count..."
ROW_COUNT=$(bq query --nouse_legacy_sql --format=csv \
    "SELECT COUNT(*) as count FROM \`$PROJECT_ID.$BQ_DATASET.$BQ_TABLE\`" 2>/dev/null | tail -1)

echo "  Rows exported: $ROW_COUNT"
echo ""

if [ "$ROW_COUNT" != "0" ] && [ -n "$ROW_COUNT" ]; then
    echo "  Running a quick sentiment summary..."
    echo ""
    bq query --nouse_legacy_sql --format=prettyjson \
        "SELECT
            COUNT(*) as total_conversations,
            ROUND(AVG(clientSentimentScore), 3) as avg_customer_sentiment,
            ROUND(AVG(agentSentimentScore), 3) as avg_agent_sentiment,
            COUNTIF(clientSentimentScore >= 0.5) as positive_conversations,
            COUNTIF(clientSentimentScore BETWEEN -0.5 AND 0.5) as neutral_conversations,
            COUNTIF(clientSentimentScore <= -0.5) as negative_conversations
        FROM \`$PROJECT_ID.$BQ_DATASET.$BQ_TABLE\`"
fi

echo ""
echo "============================================================"
echo "  EXPORT COMPLETE"
echo "============================================================"
echo ""
echo "  Your data is now in BigQuery at:"
echo "    $PROJECT_ID.$BQ_DATASET.$BQ_TABLE"
echo ""
echo "  Next: Open method5_bigquery_queries.sql in the BigQuery"
echo "  console to run turn-by-turn sentiment queries."
echo ""
echo "  BigQuery Console:"
echo "    https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo ""
