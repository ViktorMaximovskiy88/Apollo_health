#!/usr/bin/env bash
set -e

# assuming local to not create oops scenario
RESTORE_DIR=${1:?please indicate the restore directory}
DB_ENV="dev"
DB_NAME="source-hub"

mongorestore --uri="mongodb://localhost:27017/source-hub" -u admin -p admin --authenticationDatabase=admin --drop "${RESTORE_DIR}"

# careful this is for test or dev.
# mongorestore --uri="mongodb+srv://apollo-${DB_ENV}-use1-mmit-01.3qm7h.mongodb.net/${DB_NAME}?&authSource=%24external" \
#     --authenticationMechanism="MONGODB-AWS" \
#     --awsSessionToken="${AWS_SESSION_TOKEN}" \
#     -u "${AWS_ACCESS_KEY_ID}" \
#     -p "${AWS_SECRET_ACCESS_KEY}" \
#     --drop "${RESTORE_DIR}"
