#!/usr/bin/env bash
# ==============================================================================
# CCAI Insights: Prerequisites Setup Script
# ==============================================================================
#
# WHAT THIS DOES:
#   Sets up everything you need before running any of the 5 methods.
#   Run this ONCE before trying any of the analysis methods.
#
# HOW TO RUN (recommended: use Google Cloud Shell):
#
#   1. Go to https://console.cloud.google.com
#   2. Click the ">_" icon (top-right) to open Cloud Shell
#   3. Upload this project's files or clone the repo into Cloud Shell
#   4. Edit the 2 variables below — here are 3 ways to do it:
#
#      EASIEST — run these two commands (replace the values):
#        sed -i 's/your-project-id/MY-ACTUAL-PROJECT-ID/g' 00_setup.sh
#        sed -i 's/your-bucket-name/my-unique-bucket-12345/g' 00_setup.sh
#
#      OR — use the Cloud Shell editor:
#        cloudshell edit 00_setup.sh
#        (change the two values, then save with Ctrl+S)
#
#      OR — use nano (terminal text editor):
#        nano 00_setup.sh
#        (change the values, save with Ctrl+O, exit with Ctrl+X)
#
#   5. Run it:
#        chmod +x 00_setup.sh && ./00_setup.sh
#
# WHERE TO FIND YOUR PROJECT ID:
#   1. Go to https://console.cloud.google.com
#   2. Look at the top of the page — click the project dropdown
#   3. Your Project ID is the grey text under the project name
#      (often looks like: my-project-name-438291)
#   4. Copy THAT value, not the project name
#
# ==============================================================================

set -euo pipefail

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES                                                        ║
# ╚════════════════════════════════════════════════════════════════════════════╝
PROJECT_ID="your-project-id"       # <-- Replace with your GCP project ID
                                   #     Example: "ccai-demo-438291"
                                   #     Find it: project dropdown at top of console
BUCKET_NAME="your-bucket-name"     # <-- Replace with a globally unique bucket name
                                   #     Example: "my-ccai-bucket-73921"
                                   #     TIP: add random numbers to make it unique
LOCATION="us-central1"             # <-- Leave this as-is (most common region)

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  DO NOT EDIT BELOW THIS LINE (unless you know what you're doing)          ║
# ╚════════════════════════════════════════════════════════════════════════════╝

echo ""
echo "============================================================"
echo "  CCAI Insights: Prerequisites Setup"
echo "============================================================"
echo ""
echo "  Project ID:  $PROJECT_ID"
echo "  Bucket:      $BUCKET_NAME"
echo "  Location:    $LOCATION"
echo ""

# --- Preflight check ---
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "ERROR: You must edit this script and set your PROJECT_ID first."
    echo "       Open 00_setup.sh and change the PROJECT_ID variable."
    exit 1
fi

if [ "$BUCKET_NAME" = "your-bucket-name" ]; then
    echo "ERROR: You must edit this script and set your BUCKET_NAME first."
    echo "       Open 00_setup.sh and change the BUCKET_NAME variable."
    exit 1
fi

# ──────────────────────────────────────────────────────────────────────────────
# Step 1: Authenticate with Google Cloud
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 1/6: Authentication"
echo "──────────────────────────────────────────────────────────────"
echo ""

echo "Checking if you are authenticated..."
CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)

if [ -z "$CURRENT_ACCOUNT" ] || [ "$CURRENT_ACCOUNT" = "(unset)" ]; then
    echo "You are not logged in. Opening browser for authentication..."
    gcloud auth login
    gcloud auth application-default login
else
    echo "You are logged in as: $CURRENT_ACCOUNT"
    echo "(If this is wrong, run: gcloud auth login)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# Step 2: Set the project
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 2/6: Setting project to $PROJECT_ID"
echo "──────────────────────────────────────────────────────────────"
echo ""

gcloud config set project "$PROJECT_ID"
echo "Project set to: $PROJECT_ID"

# ──────────────────────────────────────────────────────────────────────────────
# Step 3: Enable all required APIs
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 3/6: Enabling required APIs (this may take a minute)"
echo "──────────────────────────────────────────────────────────────"
echo ""

echo "Enabling Contact Center AI Insights API..."
gcloud services enable contactcenterinsights.googleapis.com

echo "Enabling Cloud Storage API..."
gcloud services enable storage.googleapis.com

echo "Enabling Cloud Speech-to-Text API..."
gcloud services enable speech.googleapis.com

echo "Enabling Cloud DLP API..."
gcloud services enable dlp.googleapis.com

echo "Enabling Cloud Natural Language API..."
gcloud services enable language.googleapis.com

echo "Enabling BigQuery API (for Method 5)..."
gcloud services enable bigquery.googleapis.com

echo ""
echo "All APIs enabled."

# ──────────────────────────────────────────────────────────────────────────────
# Step 4: Create Cloud Storage bucket
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 4/6: Creating Cloud Storage bucket"
echo "──────────────────────────────────────────────────────────────"
echo ""

if gcloud storage buckets describe "gs://$BUCKET_NAME" &>/dev/null; then
    echo "Bucket gs://$BUCKET_NAME already exists. Skipping creation."
else
    echo "Creating bucket gs://$BUCKET_NAME in $LOCATION..."
    gcloud storage buckets create "gs://$BUCKET_NAME" \
        --location="$LOCATION" \
        --default-storage-class=STANDARD
    echo "Bucket created."
fi

# ──────────────────────────────────────────────────────────────────────────────
# Step 5: Upload sample conversation to GCS
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 5/6: Uploading sample conversation to Cloud Storage"
echo "──────────────────────────────────────────────────────────────"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SAMPLE_FILE="$SCRIPT_DIR/sample_conversation.json"

if [ ! -f "$SAMPLE_FILE" ]; then
    echo "ERROR: sample_conversation.json not found at $SAMPLE_FILE"
    echo "       Make sure it is in the same directory as this script."
    exit 1
fi

echo "Uploading sample_conversation.json to gs://$BUCKET_NAME/transcripts/..."
gcloud storage cp "$SAMPLE_FILE" "gs://$BUCKET_NAME/transcripts/sample_conversation.json"

echo "Verifying upload..."
gcloud storage ls "gs://$BUCKET_NAME/transcripts/"
echo "Upload complete."

# ──────────────────────────────────────────────────────────────────────────────
# Step 6: Install Python dependencies (optional)
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  Step 6/6: Python dependencies (optional)"
echo "──────────────────────────────────────────────────────────────"
echo ""

REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if command -v python3 &>/dev/null && [ -f "$REQUIREMENTS_FILE" ]; then
    read -r -p "Install Python dependencies now? (y/n): " INSTALL_PYTHON
    if [ "$INSTALL_PYTHON" = "y" ] || [ "$INSTALL_PYTHON" = "Y" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$SCRIPT_DIR/venv"
        # shellcheck disable=SC1091
        source "$SCRIPT_DIR/venv/bin/activate"
        echo "Installing packages..."
        pip install -r "$REQUIREMENTS_FILE"
        echo "Python dependencies installed in ./venv"
        echo ""
        echo "To activate the virtual environment later, run:"
        echo "  source $SCRIPT_DIR/venv/bin/activate"
    else
        echo "Skipping Python setup. You can install later with:"
        echo "  python3 -m venv venv && source venv/bin/activate"
        echo "  pip install -r requirements.txt"
    fi
else
    echo "Python 3 not found or requirements.txt missing."
    echo "You can install dependencies later for Methods 3, 4, and 5."
fi

# ──────────────────────────────────────────────────────────────────────────────
# Done!
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  SETUP COMPLETE"
echo "============================================================"
echo ""
echo "  Your environment is ready. Here is a summary:"
echo ""
echo "  Project:     $PROJECT_ID"
echo "  Bucket:      gs://$BUCKET_NAME"
echo "  Transcript:  gs://$BUCKET_NAME/transcripts/sample_conversation.json"
echo "  Location:    $LOCATION"
echo ""
echo "  Save these values — you will need them in the method scripts."
echo ""
echo "  Next steps: Pick a method and follow the instructions:"
echo "    - Method 1: Open method1_console_walkthrough.md"
echo "    - Method 2: Run ./method2_curl_pipeline.sh"
echo "    - Method 3: Run python method3_python_client.py"
echo "    - Method 4: Run python method4_devkit.py"
echo "    - Method 5: Run ./method5_bigquery_export.sh then open method5_bigquery_queries.sql"
echo ""
