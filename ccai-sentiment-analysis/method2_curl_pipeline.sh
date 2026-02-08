#!/usr/bin/env bash
# ==============================================================================
# Method 2: REST API with curl — Full End-to-End Pipeline
# ==============================================================================
#
# WHAT THIS DOES:
#   Uploads a conversation, analyzes it with sentiment + all annotators,
#   polls for completion, then retrieves and displays the results.
#   Everything is done with curl (no Python required).
#
# HOW TO RUN:
#   1. Make sure you ran 00_setup.sh first (APIs enabled, bucket created,
#      sample_conversation.json uploaded to GCS)
#
#   2. Edit the 2 variables below — EASIEST way:
#        sed -i 's/your-project-id/MY-ACTUAL-PROJECT-ID/g' method2_curl_pipeline.sh
#        sed -i 's/your-bucket-name/my-unique-bucket-12345/g' method2_curl_pipeline.sh
#
#      Or open in an editor:
#        cloudshell edit method2_curl_pipeline.sh   (Cloud Shell)
#        nano method2_curl_pipeline.sh              (terminal)
#
#   3. Run:
#        chmod +x method2_curl_pipeline.sh
#        ./method2_curl_pipeline.sh
#
#   4. Watch it go! The script handles everything automatically.
#      Results are saved to results_method2.json when done.
#
# PREREQUISITES:
#   - gcloud CLI installed and authenticated (gcloud auth login)
#     (Cloud Shell has this already)
#   - jq installed (for JSON parsing):
#       Cloud Shell:   already installed
#       Ubuntu/Debian: sudo apt-get install jq
#       macOS:         brew install jq
#
# ==============================================================================

set -euo pipefail

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE 3 VALUES                                                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝
PROJECT_ID="your-project-id"
LOCATION="us-central1"
BUCKET_NAME="your-bucket-name"

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  DO NOT EDIT BELOW THIS LINE                                              ║
# ╚════════════════════════════════════════════════════════════════════════════╝

BASE_URL="https://contactcenterinsights.googleapis.com/v1"
PARENT="projects/$PROJECT_ID/locations/$LOCATION"
GCS_TRANSCRIPT="gs://$BUCKET_NAME/transcripts/sample_conversation.json"

# ──────────────────────────────────────────────────────────────────────────────
# Helper function: get a fresh access token
# ──────────────────────────────────────────────────────────────────────────────
get_token() {
    gcloud auth print-access-token
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper function: poll an operation until it completes
# ──────────────────────────────────────────────────────────────────────────────
poll_operation() {
    local operation_name="$1"
    local description="$2"
    local max_attempts=60   # 60 attempts x 5 seconds = 5 minutes max
    local attempt=0

    echo ""
    echo "  Polling operation: $description"
    echo "  Operation: $operation_name"
    echo ""

    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))

        local response
        response=$(curl -s -X GET \
            -H "Authorization: Bearer $(get_token)" \
            "$BASE_URL/$operation_name")

        local done_status
        done_status=$(echo "$response" | jq -r '.done // false')

        if [ "$done_status" = "true" ]; then
            # Check if there was an error
            local error
            error=$(echo "$response" | jq -r '.error // empty')
            if [ -n "$error" ] && [ "$error" != "null" ]; then
                echo "  ERROR: Operation failed!"
                echo "$response" | jq '.error'
                return 1
            fi

            echo "  Done! (after $attempt polls)"
            echo "$response"
            return 0
        fi

        echo "  Waiting... attempt $attempt/$max_attempts"
        sleep 5
    done

    echo "  ERROR: Timed out after $max_attempts attempts"
    return 1
}

# ──────────────────────────────────────────────────────────────────────────────
# Preflight checks
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  CCAI Insights: Method 2 — curl REST API Pipeline"
echo "============================================================"
echo ""

if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "ERROR: Edit this script and set PROJECT_ID first."
    exit 1
fi
if [ "$BUCKET_NAME" = "your-bucket-name" ]; then
    echo "ERROR: Edit this script and set BUCKET_NAME first."
    exit 1
fi

# Check that jq is installed
if ! command -v jq &>/dev/null; then
    echo "ERROR: 'jq' is required but not installed."
    echo "  Install it with:"
    echo "    Ubuntu/Debian: sudo apt-get install jq"
    echo "    macOS:         brew install jq"
    exit 1
fi

# Check authentication
echo "Checking authentication..."
TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    echo "ERROR: Not authenticated. Run: gcloud auth login"
    exit 1
fi
echo "Authenticated. Token starts with: ${TOKEN:0:20}..."
echo ""


# ==============================================================================
# STEP 1: Upload the conversation to CX Insights
# ==============================================================================
echo ""
echo "============================================================"
echo "  STEP 1/5: Upload conversation to CX Insights"
echo "============================================================"
echo ""
echo "  Transcript: $GCS_TRANSCRIPT"
echo ""

UPLOAD_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $(get_token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{
        \"conversation\": {
            \"dataSource\": {
                \"gcsSource\": {
                    \"transcriptUri\": \"$GCS_TRANSCRIPT\"
                }
            },
            \"medium\": \"CHAT\",
            \"qualityMetadata\": {
                \"agentInfo\": [
                    {
                        \"agentId\": \"agent-001\",
                        \"displayName\": \"Support Agent\"
                    }
                ]
            }
        }
    }" \
    "$BASE_URL/$PARENT/conversations:upload")

echo "Upload response:"
echo "$UPLOAD_RESPONSE" | jq '.'

# Extract the operation name
UPLOAD_OP=$(echo "$UPLOAD_RESPONSE" | jq -r '.name')

if [ -z "$UPLOAD_OP" ] || [ "$UPLOAD_OP" = "null" ]; then
    echo "ERROR: Failed to start upload. Response:"
    echo "$UPLOAD_RESPONSE" | jq '.'
    exit 1
fi


# ==============================================================================
# STEP 2: Wait for upload to complete
# ==============================================================================
echo ""
echo "============================================================"
echo "  STEP 2/5: Waiting for upload to complete"
echo "============================================================"

UPLOAD_RESULT=$(poll_operation "$UPLOAD_OP" "Conversation upload")

# Extract the conversation name from the result
CONVERSATION_NAME=$(echo "$UPLOAD_RESULT" | jq -r '.response.name // .result.name // empty')

if [ -z "$CONVERSATION_NAME" ]; then
    echo ""
    echo "Could not extract conversation name from response."
    echo "Attempting to extract from metadata..."
    CONVERSATION_NAME=$(echo "$UPLOAD_RESULT" | jq -r '.metadata.conversationId // empty')
    if [ -z "$CONVERSATION_NAME" ]; then
        echo "Full response for debugging:"
        echo "$UPLOAD_RESULT" | jq '.'
        echo ""
        echo "TIP: You can manually list your conversations with:"
        echo "  curl -s -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
        echo "    \"$BASE_URL/$PARENT/conversations\" | jq '.conversations[].name'"
        exit 1
    fi
fi

echo ""
echo "  Conversation created: $CONVERSATION_NAME"

# Extract just the conversation ID (last part of the path)
CONVERSATION_ID=$(echo "$CONVERSATION_NAME" | awk -F'/' '{print $NF}')
echo "  Conversation ID: $CONVERSATION_ID"


# ==============================================================================
# STEP 3: Create an analysis (with ALL annotators)
# ==============================================================================
echo ""
echo "============================================================"
echo "  STEP 3/5: Analyzing conversation (all annotators)"
echo "============================================================"
echo ""
echo "  This runs: sentiment, entity, intent, silence,"
echo "  interruption, and issue model annotators."
echo ""

# Option A: Run ALL annotators (default — just send empty body)
# This is the simplest approach.
ANALYZE_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $(get_token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d '{}' \
    "$BASE_URL/$PARENT/conversations/$CONVERSATION_ID/analyses")

# ─── Alternative: Specific annotators only (uncomment to use instead) ────────
#
# ANALYZE_RESPONSE=$(curl -s -X POST \
#     -H "Authorization: Bearer $(get_token)" \
#     -H "Content-Type: application/json; charset=utf-8" \
#     -d '{
#         "annotatorSelector": {
#             "runSentimentAnnotator": true,
#             "runEntityAnnotator": true,
#             "runIntentAnnotator": true,
#             "runSilenceAnnotator": true,
#             "runInterruptionAnnotator": true,
#             "runIssueModelAnnotator": true
#         }
#     }' \
#     "$BASE_URL/$PARENT/conversations/$CONVERSATION_ID/analyses")
#
# ─── Alternative: Sentiment ONLY (uncomment to use instead) ──────────────────
#
# ANALYZE_RESPONSE=$(curl -s -X POST \
#     -H "Authorization: Bearer $(get_token)" \
#     -H "Content-Type: application/json; charset=utf-8" \
#     -d '{
#         "annotatorSelector": {
#             "runSentimentAnnotator": true
#         }
#     }' \
#     "$BASE_URL/$PARENT/conversations/$CONVERSATION_ID/analyses")

echo "Analysis response:"
echo "$ANALYZE_RESPONSE" | jq '.'

ANALYSIS_OP=$(echo "$ANALYZE_RESPONSE" | jq -r '.name')

if [ -z "$ANALYSIS_OP" ] || [ "$ANALYSIS_OP" = "null" ]; then
    echo "ERROR: Failed to start analysis."
    exit 1
fi


# ==============================================================================
# STEP 4: Wait for analysis to complete
# ==============================================================================
echo ""
echo "============================================================"
echo "  STEP 4/5: Waiting for analysis to complete"
echo "============================================================"

ANALYSIS_RESULT=$(poll_operation "$ANALYSIS_OP" "Conversation analysis")

echo ""
echo "  Analysis complete!"


# ==============================================================================
# STEP 5: Retrieve and display results
# ==============================================================================
echo ""
echo "============================================================"
echo "  STEP 5/5: Retrieving full results"
echo "============================================================"
echo ""

# 5a: Get the full conversation (includes latest analysis)
echo "Fetching full conversation with annotations..."
echo ""

FULL_CONVERSATION=$(curl -s -X GET \
    -H "Authorization: Bearer $(get_token)" \
    "$BASE_URL/$PARENT/conversations/$CONVERSATION_ID")

# ── Display: Conversation-Level Sentiment ──────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  CONVERSATION-LEVEL SENTIMENT                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "$FULL_CONVERSATION" | jq -r '
    .latestAnalysis.analysisResult.callAnalysisMetadata.sentiments[]? |
    "  Channel \(.channelTag): score=\(.sentimentData.score), magnitude=\(.sentimentData.magnitude)"
'

# ── Display: Turn-by-Turn Sentiment (from annotations) ────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  TURN-BY-TURN SENTIMENT ANNOTATIONS                            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "$FULL_CONVERSATION" | jq -r '
    .latestAnalysis.analysisResult.callAnalysisMetadata.annotations[]?
    | select(.sentimentData != null)
    | "  Turn (Channel \(.channelTag)): score=\(.sentimentData.score), magnitude=\(.sentimentData.magnitude)"
'

# ── Display: Entity Annotations ──────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ENTITY EXTRACTION                                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "$FULL_CONVERSATION" | jq -r '
    .latestAnalysis.analysisResult.callAnalysisMetadata.entities // {} | to_entries[]? |
    "  Entity: \(.key) (type=\(.value.type))"
'

# ── Display: Intent Detection ────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  INTENT DETECTION                                               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "$FULL_CONVERSATION" | jq -r '
    .latestAnalysis.analysisResult.callAnalysisMetadata.intents // {} | to_entries[]? |
    "  Intent: \(.key) (id=\(.value.id))"
'

# ── Display: Issue/Topic Detection ───────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ISSUE/TOPIC DETECTION                                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "$FULL_CONVERSATION" | jq -r '
    .latestAnalysis.analysisResult.callAnalysisMetadata.issueModelResult.issues[]? |
    "  Issue: \(.issue) (score=\(.score))"
'

# ── Save raw results to file ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/results_method2.json"
echo "$FULL_CONVERSATION" | jq '.' > "$OUTPUT_FILE"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  COMPLETE                                                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Full results saved to: $OUTPUT_FILE"
echo ""
echo "  To explore the results interactively:"
echo "    cat $OUTPUT_FILE | jq '.latestAnalysis.analysisResult.callAnalysisMetadata'"
echo ""
echo "  To see only sentiment annotations:"
echo "    cat $OUTPUT_FILE | jq '.latestAnalysis.analysisResult.callAnalysisMetadata.annotations[] | select(.sentimentData != null)'"
echo ""
echo "  To see the transcript:"
echo "    cat $OUTPUT_FILE | jq '.transcript.transcriptSegments[]'"
echo ""

# ── Bonus: Show how to manually do each step separately ──────────────────
echo ""
echo "============================================================"
echo "  CHEAT SHEET: Individual curl commands"
echo "============================================================"
echo ""
echo "  # List all conversations:"
echo "  curl -s -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "    \"$BASE_URL/$PARENT/conversations\" | jq '.conversations[].name'"
echo ""
echo "  # Get a specific conversation:"
echo "  curl -s -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "    \"$BASE_URL/$PARENT/conversations/$CONVERSATION_ID\" | jq '.'"
echo ""
echo "  # List analyses for a conversation:"
echo "  curl -s -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "    \"$BASE_URL/$PARENT/conversations/$CONVERSATION_ID/analyses\" | jq '.'"
echo ""
echo "  # Run a new analysis (sentiment only):"
echo "  curl -s -X POST \\"
echo "    -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"annotatorSelector\":{\"runSentimentAnnotator\":true}}' \\"
echo "    \"$BASE_URL/$PARENT/conversations/$CONVERSATION_ID/analyses\""
echo ""
echo "  # Delete a conversation:"
echo "  curl -s -X DELETE \\"
echo "    -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
echo "    \"$BASE_URL/$PARENT/conversations/$CONVERSATION_ID\""
echo ""
