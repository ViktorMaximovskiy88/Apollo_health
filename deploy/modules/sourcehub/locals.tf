locals {
  app_name     = "apollo"
  service_name = "sourcehub"

  short_regions = {
    "us-west-2" : "usw2",
    "us-east-1" : "use1",
    "us-east-2" : "use2",
    "us-west-1" : "usw1"
  }

  short_region = local.short_regions[var.region]

  effective_tags = merge(var.tags, {
    environment = var.environment
    service     = local.service_name
  })

  target_azs = {
    "sbx" : [
      "${var.region}b",
      "${var.region}c"
    ],
    "dev" : [
      "${var.region}b",
      "${var.region}c"
    ],
    "tst" : [
      "${var.region}c",
      "${var.region}d"
    ],
    "prd" : [
      "${var.region}a",
      "${var.region}b"
    ]

  }

  ##
  # VPCs are scoped to the AWS Account, NOT the Apollo environment
  # This mapping will map the Apollo Environment to the VPC Environment
  ##
  vpc_env_mapping = {
    "sbx": "dev"
    "dev": "dev"
    "tst": "tst"
    "prd": "prd"
  }
  vpc_environment = local.vpc_env_mapping[var.environment]
  
  event_source = "com.mmitnetwork.sourcehub"

  # Will leave the base mongodb-url unchanged in case other apps need a different auth mechanism
  # For SourceHub, add the authMechanism
  mongodb_url = "${data.aws_ssm_parameter.mongodb-url.value}&authMechanism=MONGODB-AWS&authSource=$external"
  mongodb_db  = "source-hub"

  new_relic_app_name = "${title(local.app_name)}-${title(var.environment)}-${title(local.service_name)}"

  new_relic_secrets = [
    {
      name      = "NEW_RELIC_LICENSE_KEY"
      valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/${var.environment}/new_relic_license_key"
    },
    {
      name      = "NEW_RELIC_API_KEY"
      valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/${var.environment}/new_relic_api_key"
    }
  ]

  ##
  # DNS Domains are scoped to the AWS Account, NOT the Apollo environment
  # This mapping will map the Apollo Enviroment to the DNS Host
  ##
  dns_host_env_mapping = {
    "sbx": "sourcehub-sbx.dev.mmitnetwork.com"
    "dev": "sourcehub.dev.mmitnetwork.com"
    "tst": "sourcehub.test.mmitnetwork.com"
    "prd": "sourcehub.mmitnetwork.com"
  }
  dns_host = local.dns_host_env_mapping[var.environment]
}