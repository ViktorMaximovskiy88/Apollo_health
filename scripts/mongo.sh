#!/usr/bin/env bash


SCRIPT_NAME=${1:?please provide script name}

mongosh \
    -u "admin" \
    -p "admin" \
    --authenticationDatabase="admin" \
    "mongodb://localhost:27017/source-hub" \
    "${SCRIPT_NAME}"

# AWS_ACCESS_KEY_ID=""
# AWS_SECRET_ACCESS_KEY=""
# AWS_SESSION_TOKEN=""

# bash doesnt do this well on mac, you can use encodeURIComponent($AWS_SESSION_TOKEN)
# AWS_SESSION_TOKEN_URL_ENCODED=""
# mongosh \
#     -u "${AWS_ACCESS_KEY_ID}" \
#     -p "${AWS_SECRET_ACCESS_KEY}" \
#     "mongodb+srv://apollo-dev-use1-mmit-01.3qm7h.mongodb.net/source-hub?authSource=%24external&authMechanism=MONGODB-AWS&authMechanismProperties=AWS_SESSION_TOKEN:${AWS_SESSION_TOKEN_URL_ENCODED}" \
#     --eval "${COLLECTIONS}"