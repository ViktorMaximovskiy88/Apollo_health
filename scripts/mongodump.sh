#!/usr/bin/env bash

# assuming local to not create oops scenario
rm -rf ./dump
mongodump --uri="mongodb://localhost:27017/source-hub" -u admin -p admin --authenticationDatabase=admin