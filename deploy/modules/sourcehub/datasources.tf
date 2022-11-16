data "aws_caller_identity" "current" {
}

data "aws_subnet" "first-app-subnet" {
  id = data.aws_subnets.app-subnet-ids.ids[0]
  tags = {
    subnet_role = "app"
    environment = var.environment
  }
}

data "aws_subnets" "app-subnet-ids" {
  tags = {
    subnet_role = "app"
    environment = var.environment
  }
}

# TODO: Revisit, don't want to look up by name
data "aws_iam_role" "ecs-execution" {
  name = format("%s-%s-ecsexec-%s-mmit-role-%02d", local.app_name, var.environment, local.short_region, var.revision)
  # tags = {
  #   environment = var.environment
  #   project = local.app_name
  #   role = "ecs-execution"
  # }
  
}

data "aws_security_group" "alb-public" {
  vpc_id = data.aws_subnet.first-app-subnet.vpc_id
  tags = {
    environment = var.environment
    project = local.app_name
    security_group_role = "public"
  }
}

# TODO: Revisit, don't want to look up by name
data "aws_ecs_cluster" "ecs-cluster" {
  cluster_name = format("%s-%s-%s-mmit-ecs-%02d", local.app_name, var.environment, local.short_region, var.revision)
  # tags = {
  #   environment = var.environment
  #   project = local.app_name
  # }
}

data "aws_ecr_repository" "sourcehub-app" {
  name = "sourcehub-app"  
}

data "aws_lb" "alb" {  
  tags = {
    environment = var.environment
    project = local.app_name
  }
}

data "aws_lb_listener" "http" {
  
  port = 80
  load_balancer_arn = data.aws_lb.alb.arn

  tags = {
    environment = var.environment
    project = local.app_name
  }
}

data "aws_lb_listener" "https" {
  
  port = 443
  load_balancer_arn = data.aws_lb.alb.arn

  tags = {
    environment = var.environment
    project = local.app_name
  }
}

# TODO: Revisit, don't want to look up by name
data "aws_iam_policy" "docrepo-contributor" {
  name = format("%s-%s-docrepo-contributor-mmit-policy-%02d", local.app_name, var.environment, var.revision)
}

data "aws_iam_policy" "sourcehub-eventbus-contributor" {
  name = format("%s-%s-%s-eventbus-contributor-mmit-policy-%02d", local.app_name, var.environment, local.service_name, var.revision)
}

data "aws_service" "s3" {
  service_id = "s3"
}

# TODO: Revisit, don't want to look up by name
data "aws_ecs_cluster" "cluster" {
  cluster_name = format("%s-%s-%s-mmit-ecs-%02d", local.app_name, var.environment, local.short_region, var.revision)
}

data "aws_ssm_parameter" "mongodb-url" {
  name = "/apollo/mongodb_url"
}

data "aws_ssm_parameter" "redis-url" {
  name = "/apollo/redis_url"
}

data "aws_ssm_parameter" "docrepo-bucket-name" {
  name = "/apollo/docrepo_bucket_name"
}

data "aws_ssm_parameter" "smartproxy-username" {
  name = "/apollo/smartproxy_username"
}

data "aws_cloudwatch_event_bus" "sourcehub" {
  name = format("%s-%s-%s-%s-mmit-bus-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
}
