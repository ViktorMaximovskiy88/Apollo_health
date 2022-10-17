#!/usr/bin/env bash

# todo format later
COLLECTIONS=$(cat <<-END
    db.ChangeLog.drop();
    db.Comment.drop();
    db.ContentExtractionResult.drop();
    db.ContentExtractionTask.drop();
    db.DocDocument.drop();
    db.DocumentAnalysis.drop();
    db.LinkTaskLog.drop();
    db.RetrievedDocument.drop();
    db.SiteScrapeTask.drop();
END
)

mongosh -u admin -p admin --authenticationDatabase=admin mongodb://localhost:27017/source-hub --eval "${COLLECTIONS}"

# AWS_ACCESS_KEY_ID=""
# AWS_SECRET_ACCESS_KEY=""
# AWS_SESSION_TOKEN=""
# AWS_SESSION_TOKEN_URL_ENCODED="" # bash doesnt do this well on mac, you can use encodeURIComponent for the same for now
# mongosh -u $AWS_ACCESS_KEY_ID -p $AWS_SECRET_ACCESS_KEY  "mongodb+srv://apollo-dev-use1-mmit-01.3qm7h.mongodb.net/source-hub?authSource=%24external&authMechanism=MONGODB-AWS&authMechanismProperties=AWS_SESSION_TOKEN:${AWS_SESSION_TOKEN_URL_ENCODED}" --eval "${COLLECTIONS}"