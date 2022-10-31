#!/usr/bin/env bash

# Examples
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 documents/63e01ca7c256e0e398d4f72309eb33ab.pdf
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 text/2c672985e12a5e3ceeb69703ea8a1593.txt

S3_BUCKET=${1:?specifybucket}
S3_KEY=${2:?specifykey}

mkdir -p "./tmp/${S3_BUCKET}/documents"
mkdir -p "./tmp/${S3_BUCKET}/text"
mkdir -p "./tmp/${S3_BUCKET}/diffs"

DOWNLOAD_PATH="./tmp/${S3_BUCKET}/${S3_KEY}"
aws s3api get-object --bucket "${S3_BUCKET}" --key "${S3_KEY}" "${DOWNLOAD_PATH}"