db.Proxy.updateMany(
  {},
  {
    $set: { endpoints: [] },
  }
);

db.Site.updateMany(
  {},
  {
    $set: { last_run_status: null, last_run_time: null, last_run_documents: 0 },
  }
);
