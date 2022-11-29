region   = "us-east-1"
revision = 1

environment = "prd"

# Revisit to inject tag and not use latest
sourcehub-app-version          = "latest"
sourcehub-scrapeworker-version = "latest"
sourcehub-parseworker-version  = "latest"
sourcehub-scheduler-version    = "latest"
sourcehub-taskworker-version   = "latest"

auth0-config = {
  domain        = "https://mmitnetwork.auth0.com"
  client_id     = "PLx3LGXqzvmwJkx21a6yno0RDHf5q7w9"
  audience      = "http://localhost:8000/api/v1"
  wellknown_url = "https://mmitnetwork.auth0.com/.well-known/jwks.json"
  issuer        = "https://mmitnetwork.auth0.com/"
}
