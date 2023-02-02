terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.51.0"
    }
  }
}

##
# Deprecated
##
resource "aws_iam_service_linked_role" "autoscaling" {
  count = var.environment == "sbx" ? 0 : 1
  aws_service_name = "autoscaling.amazonaws.com"
}

resource "aws_iam_service_linked_role" "autoscaling2" {
  aws_service_name = "autoscaling.amazonaws.com"
  custom_suffix = var.environment
}