terraform {
  source = "${path_relative_from_include()}/../modules//sourcehub"
  
}

generate "backend" {
  path = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
terraform {
    backend "s3" {}
}
EOF
}

generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
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
EOF
}

inputs = {
  region = "us-east-1"
  revision = 1
  
}