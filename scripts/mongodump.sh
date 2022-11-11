#!/usr/bin/env bash
set -e

DB_ENV="prd"
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

# mongodump --uri="mongodb://localhost:27017/${DB_NAME}" \
#     -u "admin" \
#     -p "admin" \
#     --authenticationDatabase="admin" \
#     -o "${BACKUP_NAME}"

export AWS_ACCESS_KEY_ID="ASIAZHK2DEJDI7AN3TEJ"
export AWS_SECRET_ACCESS_KEY="gg1BwuLZ/r0HevSvqitDzr2PgSJOvs2xMdTE9z6L"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEJv//////////wEaCXVzLWVhc3QtMSJIMEYCIQDWO2uLYa2Gj5ju0tN85hWSI2hR8aHDEy4FDgUj8wNxhQIhAJw+SONgxdomFzWWAQEb2TxV0zxHZ6+3Xj+atqS3yWcCKqADCJP//////////wEQARoMNjM0MjMzNDk2MTM0IgyG0ec2UFVLQS4EE3Mq9AIyWvCSo02JLMLOJJsSiPA1NV0AGmfkLJtKi6Ij3dnm17Rkoh8iZXmzlekGWhcGKQHhr6rqZZzxvrS2+c9qBKDyBPTb351zp1QAph6bGPgTd26xd5VECbCg17OQwLlLdJ+fuIo8SyuyVL6eGrurV1HclKJoDCUenrnCsiZAVagGFI6QchFICP5UvDsjlMIf5EzKukXFgAbjAmTfz4yBF7Xsy4zLjRkHftsumD6Ti5n+LoQCmZugk1w/1lXZI43Q1mj4OoPLi6tBSi3S5EVQCcwOXi+z5me5B4Fz8L02MYZNBMGAEexL57JgTMQlwPRuIJ/LKMOyefw98qLktxTU/acetlm6nIwyKzXZ5dzw+VkrFDBqSSC2jCJ1n4DqblksDLSHed8jSFdk036qcxQAsOEetni3Kp6kBc0TrhRoj4ikz0VbKl0K8d+w6cmzZkbFjFaXjUuHJgGHJ5Z1T+ch/+J9lC1b//d28LaIguvsZkhVgGgfdRowuKK6mwY6pQFM5edR0fX9ZOwterTsQ0jIxWWsI3JrQ8+v0dJaDr6lcBMK3Ccs+RX0ppXlFU10XTmcsh5FfOlKdnz3APT2rqpNgcTOkDHfdYcr64g7QI+EEB/2TFPLjQtfg77J0MX8BmOwi34ZEiwngsyuEgbn1PBeBfOYVpL8w9KKqqCmOqAKOp/Xxt9cg1lWLOFy4TWpldcdqcRk3q712okjOHeF3jX3nrVItA4="

# careful this is for test or dev.
mongodump --uri="mongodb+srv://apollo-${DB_ENV}-use1-mmit-01.3qm7h.mongodb.net/${DB_NAME}?&authSource=%24external" \
    --authenticationMechanism="MONGODB-AWS" \
    --awsSessionToken="${AWS_SESSION_TOKEN}" \
    -u "${AWS_ACCESS_KEY_ID}" \
    -p "${AWS_SECRET_ACCESS_KEY}" \
    -o "${BACKUP_NAME}" \
    --excludeCollection "ChangeLog" \
    --excludeCollection "LinkTaskLog"

# echo "Archiving backup to ${ARCHIVE_NAME}"
# tar -czf "${ARCHIVE_NAME}" "${BACKUP_NAME}"
# echo "Backup & archive complete"
