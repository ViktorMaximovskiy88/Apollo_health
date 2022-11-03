#!/usr/bin/env bash
set -e

DB_ENV="tst"
DB_NAME="source-hub"
TIMESTAMP=$(date +'%Y%m%d_%H%M%S_%Z')
OUTPUT_NAME="${DB_NAME}-${DB_ENV}-${TIMESTAMP}"

# assuming local to not create oops scenario
BACKUP_PATH="./dump"
BACKUP_NAME="${BACKUP_PATH}/${OUTPUT_NAME}"
mkdir -p "${BACKUP_PATH}"

ARCHIVE_PATH="${HOME}/archives"
mkdir -p "${ARCHIVE_PATH}"
ARCHIVE_NAME="${ARCHIVE_PATH}/${OUTPUT_NAME}.tgz"

mongodump --uri="mongodb://localhost:27017/${DB_NAME}" \
    -u "admin" \
    -p "admin" \
    --authenticationDatabase="admin" \
    -o "${BACKUP_NAME}"

# careful this is for test or dev.
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_SESSION_TOKEN=""

# mongodump --uri="mongodb+srv://apollo-${DB_ENV}-use1-mmit-01.3qm7h.mongodb.net/${DB_NAME}?&authSource=%24external" \
#     --authenticationMechanism="MONGODB-AWS" \
#     --awsSessionToken="${AWS_SESSION_TOKEN}" \
#     -u "${AWS_ACCESS_KEY_ID}" \
#     -p "${AWS_SECRET_ACCESS_KEY}" \
#     -o "${BACKUP_NAME}" \
#     --excludeCollection "ChangeLog"

echo "Archiving backup to ${ARCHIVE_NAME}"
tar -czf "${ARCHIVE_NAME}" "${BACKUP_NAME}"
echo "Backup & archive complete"
