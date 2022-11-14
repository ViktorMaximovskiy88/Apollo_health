terraform {
  backend "s3" {
  }
}

module "sourcehub" {
  source = "../modules//sourcehub"

  region   = var.region
  revision = var.revision

  environment                    = var.environment
  sourcehub-app-version          = var.sourcehub-app-version
  sourcehub-scrapeworker-version = var.sourcehub-scrapeworker-version
  sourcehub-parseworker-version  = var.sourcehub-parseworker-version
  sourcehub-scheduler-version    = var.sourcehub-scheduler-version
  sourcehub-dbmigrations-version = var.sourcehub-dbmigrations-version
  sourcehub-lineageworker-version = var.sourcehub-lineageworker-version
  sourcehub-pdfdiffworker-version = var.sourcehub-pdfdiffworker-version

  auth0-config = var.auth0-config
}
