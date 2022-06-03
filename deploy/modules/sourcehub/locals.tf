locals {
  app_name = "apollo"
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
    service  = local.service_name
  })

  target_azs = {
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
}