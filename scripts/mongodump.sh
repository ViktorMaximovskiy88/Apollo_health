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

# mongodump --uri="mongodb://localhost:27017/${DB_NAME}" \
#     -u "admin" \
#     -p "admin" \
#     --authenticationDatabase="admin" \
#     -o "${BACKUP_NAME}"

# careful this is for test or dev.
export AWS_ACCESS_KEY_ID="ASIAUSADWD3QNZOLM2M7"
export AWS_SECRET_ACCESS_KEY="4Yc/7eCyYYVddbKWh82m5lmuK20V5fRgYe4B2N7G"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEDcaCXVzLWVhc3QtMSJIMEYCIQCZ7BSa0AoLXXabKaDmfuyUZb5pBzY7y597+W9TV5kecAIhAPqT4oGNM9/8ftuwkbevSA/965bKsJxg3UtlToVRy3mjKpcDCC8QABoMMzEzNTQwMzUzNzYwIgyW+mjytM0DgJyIycQq9AKPb0VanU1u/wTv6n6BigvXRyyYlrkSiMsZzfoJUaW1zUaFe/tfd/VHRshAb8Rlhd4Z8WpuR2c2sYM1QBR7s8vEcoCAEo0g28/BZ/PTbwKP/amprTAqCemB9Ye4fu0u2gU3VAsXpKiz4tLHIQSXD4LeTgeJNZrSgtv3lPLJlpsPMmM6+N7nDnKqlz/9CPEXE3maMDvD2CX26gmmtHu7yxL3N6X8Uedcm2fts5DyLpqYff5Pkbu0vcNuKM20tngMwMO37OmGrYZA8hEL/EU5lOzAdPvpZR6pcUnf40XehzqsLIOaQwVoDvSolBq+UHgf58Nbwk70q8rSuIF4UNMiWr+boqi2euHwaCqD1FM5nZaIzgTob93LPGeoXxQaRTBsIfbn4ObhFS3OYThYRxSAa8xe44pVgb9/tojrvNAFOsKneW5BklJY77ecmsK7WcImBtakyaUVQFvHFbMR5qWFR95/4hh+8rU20Dsmag5ct8ZIOd6JQAowyaSkmwY6pQH3nyp1/i80kIAUKhNSp7Wvcc26SI4kfLMgexFE0gIch5xDrkRuQn8ToVwijSjYXfUVmxslVjUn0ODDfwjCrANLvm+dUrmVsji/1F0PNbUxav03zXifQKih0Xfw3fknvJtJrzJ0aoSabjetQjKVx03I36OalP1Y/i97BXx/pbyTXwhDprYpS8g5ghmSKrseV5RDPc6bW7IhVAsh3AkKfVu0Sp8Nsvo="

mongodump --uri="mongodb+srv://apollo-${DB_ENV}-use1-mmit-01.3qm7h.mongodb.net/${DB_NAME}?&authSource=%24external" \
    --authenticationMechanism="MONGODB-AWS" \
    --awsSessionToken="${AWS_SESSION_TOKEN}" \
    -u "${AWS_ACCESS_KEY_ID}" \
    -p "${AWS_SECRET_ACCESS_KEY}" \
    -o "${BACKUP_NAME}" \
    --excludeCollection "ChangeLog"

echo "Archiving backup to ${ARCHIVE_NAME}"
tar -czf "${ARCHIVE_NAME}" "${BACKUP_NAME}"
echo "Backup & archive complete"
