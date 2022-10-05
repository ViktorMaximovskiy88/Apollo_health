#!/usr/bin/env bash

# todo format later
COLLECTIONS=$(cat <<-END
    db.DocumentAnalysis.drop();
    db.RetrievedDocument.drop();
    db.SiteScrapeTask.drop();
    db.DocDocument.drop();
END
)

mongosh -u admin -p admin --authenticationDatabase=admin mongodb://localhost:27017/source-hub --eval "${COLLECTIONS}"
