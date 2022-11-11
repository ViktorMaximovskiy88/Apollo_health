#!/usr/bin/env bash

# Examples
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 documents/3fc06e62a1d9a9e8d75e57421c4aab0d.pdf
# ./scripts/s3-fetch.sh apollo-dev-docrepo-use1-mmit-s3-01 text/42cb06a528369deff92e6419c88401a7.txt

S3_BUCKET=${1:?specifybucket}
S3_KEY=${2:?specifykey}

mkdir -p "./tmp/${S3_BUCKET}/documents"
mkdir -p "./tmp/${S3_BUCKET}/text"
mkdir -p "./tmp/${S3_BUCKET}/diffs"

DOWNLOAD_PATH="./tmp/${S3_BUCKET}/${S3_KEY}"
aws s3api get-object --bucket "${S3_BUCKET}" --key "${S3_KEY}" "${DOWNLOAD_PATH}"