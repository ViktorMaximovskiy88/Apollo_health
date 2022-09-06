#!/usr/bin/env bash

# assuming local to not create oops scenario

mongorestore --uri="mongodb://localhost:27017/source-hub" -u admin -p admin --authenticationDatabase=admin --drop ./dump/source-hub