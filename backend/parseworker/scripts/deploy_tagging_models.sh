#! /bin/bash
set -e

export MODEL_VERSION="2023XXXX.1"
export MONGO_DB="source-hub"
export S3_ENDPOINT_URL="s3.us-east-1.amazonaws.com"

# Paste in Dev creds here
export ENV_TYPE="dev"
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""
export S3_DOCUMENT_BUCKET="apollo-dev-docrepo-use1-mmit-s3-01"
export MONGO_URL="mongodb+srv://apollo-dev-use1-mmit-01.3qm7h.mongodb.net/?retryWrites=true&w=majority&authMechanism=MONGODB-AWS&authSource=\$external"
python backend/parseworker/scripts/upload_tagging_models.py $MODEL_VERSION
python backend/parseworker/scripts/set_tagging_model_version.py $MODEL_VERSION

# Paste in Test creds here
ENV_TYPE="tst"
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""
export S3_DOCUMENT_BUCKET="apollo-tst-docrepo-use1-mmit-s3-01"
export MONGO_URL="mongodb+srv://apollo-tst-use1-mmit-01.3qm7h.mongodb.net/?retryWrites=true&w=majority&authMechanism=MONGODB-AWS&authSource=\$external"
python backend/parseworker/scripts/upload_tagging_models.py $MODEL_VERSION
python backend/parseworker/scripts/set_tagging_model_version.py $MODEL_VERSION

# Paste in Prod creds here
ENV_TYPE="prd"
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""
export S3_DOCUMENT_BUCKET="apollo-prd-docrepo-use1-mmit-s3-01"
export MONGO_URL="mongodb+srv://apollo-prd-use1-mmit-01.3qm7h.mongodb.net/?retryWrites=true&w=majority&authMechanism=MONGODB-AWS&authSource=\$external"
python backend/parseworker/scripts/upload_tagging_models.py $MODEL_VERSION
python backend/parseworker/scripts/set_tagging_model_version.py $MODEL_VERSION


rm -rf $MODEL_VERSION