provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = merge(var.tags, {
      cloud    = "AWS"
      company  = "MMIT"
      project  = "apollo"
      revision = var.revision
      region   = var.region
    })
  }
}