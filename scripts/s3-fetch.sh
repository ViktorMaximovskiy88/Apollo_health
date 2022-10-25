#!/usr/bin/env bash

# Examples
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 text/00003cf5099980405245d424bab1547e.txt
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 documents/ce0c50a0c3dcf86542f18b4c6bb8ec15.pdf

S3_BUCKET=${1:?specifybucket}
S3_KEY=${2:?specifykey}

mkdir -p "./tmp/${S3_BUCKET}/documents"
mkdir -p "./tmp/${S3_BUCKET}/text"
mkdir -p "./tmp/${S3_BUCKET}/diffs"

DOWNLOAD_PATH="./tmp/${S3_BUCKET}/${S3_KEY}"
aws s3api get-object --bucket "${S3_BUCKET}" --key "${S3_KEY}" "${DOWNLOAD_PATH}"