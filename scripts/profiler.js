db.setProfilingLevel(2);

printjson(db.system.profile.find().sort({ ts: -1 }).limit(1).pretty());
