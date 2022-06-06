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
}
