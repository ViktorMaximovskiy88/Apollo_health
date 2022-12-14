db.ChangeLog.drop();
db.Comment.drop();
db.ContentExtractionResult.drop();
db.ContentExtractionTask.drop();
db.DocDocument.drop();
db.DocumentAnalysis.drop();
db.LinkTaskLog.drop();
db.RetrievedDocument.drop();
db.SiteScrapeTask.drop();
db.TaskLog.drop();

// reset scrape data at site level too
db.Site.updateMany(
  {},
  {
    $set: { last_run_status: null, last_run_time: null, last_run_documents: 0 },
  }
);
