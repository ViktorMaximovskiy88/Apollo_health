#!/usr/bin/env bash

# assuming local to not create oops scenario
RESTORE_DIR=${1:?please indicate the restore directory}
mongorestore --uri="mongodb://localhost:27017/source-hub" -u admin -p admin --authenticationDatabase=admin --drop "${RESTORE_DIR}"
