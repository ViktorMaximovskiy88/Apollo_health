#!/usr/bin/env bash

# todo format later
mongosh -u admin -p admin --authenticationDatabase=admin mongodb://localhost:27017/source-hub --eval "db.Lineage.drop();db.LineageCompare.drop();"
