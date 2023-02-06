region   = "us-east-1"
revision = 1

environment                    = "sbx"
sourcehub-app-version          = "latest"
sourcehub-scrapeworker-version = "latest"
sourcehub-parseworker-version  = "latest"
sourcehub-scheduler-version    = "latest"
sourcehub-taskworker-version   = "latest"

auth0-config = {
  domain        = "https://mmit-test.auth0.com"
  client_id     = "7iS7ZzJYlOe8y1U3Vrj4zIDKIhqKD2HK"
  audience      = "http://localhost:8000/api/v1"
  wellknown_url = "https://mmit-test.auth0.com/.well-known/jwks.json"
  issuer        = "https://mmit-test.auth0.com/"
}
