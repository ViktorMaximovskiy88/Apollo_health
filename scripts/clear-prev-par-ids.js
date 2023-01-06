db.DocDocument.updateMany(
  {},
  {
    $set: { previous_par_id: null },
  }
);

db.ChangeLog.updateMany(
  { "delta.path": "/previous_par_id" },
  {
    $pull: {
      delta: { path: "/previous_par_id" },
    },
  }
);
