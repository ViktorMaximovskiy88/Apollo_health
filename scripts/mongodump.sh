#!/usr/bin/env bash

# assuming local to not create oops scenario
rm -rf ./dump
mongodump --uri="mongodb://localhost:27017/source-hub" -u admin -p admin --authenticationDatabase=admin

# careful
# AWS_ACCESS_KEY_ID=""
# AWS_SECRET_ACCESS_KEY=""
# AWS_SESSION_TOKEN=""
# mongodump --uri="mongodb+srv://apollo-dev-use1-mmit-01.3qm7h.mongodb.net/source-hub?&authSource=%24external" --authenticationMechanism=MONGODB-AWS --awsSessionToken=$AWS_SESSION_TOKEN -u $AWS_ACCESS_KEY_ID -p $AWS_SECRET_ACCESS_KEY --excludeCollection ChangeLog --excludeCollection LinkTaskLog