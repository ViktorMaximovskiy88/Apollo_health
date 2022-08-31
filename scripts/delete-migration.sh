#!/usr/bin/env bash


name=${1:?}
mongosh -u admin -p admin --authenticationDatabase=admin mongodb://localhost:27017/source-hub --eval "db.migrations_log.remove({ \"name\": \"${name}\" })"
