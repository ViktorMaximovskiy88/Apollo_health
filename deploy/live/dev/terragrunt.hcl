include "root" {
  path = find_in_parent_folders()
}

remote_state {
  backend = "s3"
  config = {
    bucket = "tf-state-dev-apollo-use1-mmit-s3-01"
    key = "sourcehub-app/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "tf-state-dev-apollo-use1-mmit-ddbtable-01"
    profile = "MMIT-Dev"
  }
}

inputs = {
  environment = "dev"
  sourcehub-app-version = "latest"
}

