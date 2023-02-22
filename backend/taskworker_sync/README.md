# Taskworker Sync Function

A lambda function triggered by the Taskworker DLQ. The dependencies are not shared with the root folders poetry file.

## Env Setup

We are using a separate virtual environment to reduce the size of our dependencies. Furthermore, we are using pip for simplicity. As of right now, this is designed to run on docker-compose up.

### Testing

Rudimentary testing via curl (assumes your docker is running):

```bash
curl -XPOST "http://localhost:7070/2015-03-31/functions/function/invocations" -d @./backend/taskworker_sync/sample_event.json
```
