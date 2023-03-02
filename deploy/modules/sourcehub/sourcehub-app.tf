resource "aws_cloudwatch_log_group" "app" {
  name = format("/%s/%s-%s-app", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-app"
  })
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.service_name}-app-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  # TODO: Make cpu, memory a variable and determine appropriate thresholds
  cpu    = 1024
  memory = 2048


  container_definitions = jsonencode([
    {
      name  = "${local.service_name}-app"
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-app-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && python app/main.py"
      ]
      environment = [
        {
          name  = "ENV_TYPE"
          value = var.environment
        },
        {
          name  = "S3_ENDPOINT_URL"
          value = data.aws_service.s3.dns_name
        },
        {
          name  = "MONGO_URL"
          value = local.mongodb_url
        },
        {
          name  = "MONGO_DB"
          value = local.mongodb_db
        },
        {
          name  = "REDIS_URL"
          value = data.aws_ssm_parameter.redis-url.value
        },
        {
          name  = "S3_DOCUMENT_BUCKET"
          value = data.aws_ssm_parameter.docrepo-bucket-name.value
        },
        {
          name  = "REACT_APP_AUTH0_DOMAIN"
          value = var.auth0-config.domain
        },
        {
          name  = "REACT_APP_AUTH0_CLIENT_ID"
          value = var.auth0-config.client_id
        },
        {
          name  = "REACT_APP_AUTH0_AUDIENCE"
          value = var.auth0-config.audience
        },
        {
          name  = "AUTH0_WELLKNOWN_URL"
          value = var.auth0-config.wellknown_url
        },
        {
          name  = "AUTH0_AUDIENCE"
          value = var.auth0-config.audience
        },
        {
          name  = "AUTH0_ISSUER"
          value = var.auth0-config.issuer
        },
        {
          name  = "EVENT_BUS_ARN"
          value = data.aws_cloudwatch_event_bus.sourcehub.arn
        },
        {
          name  = "EVENT_SOURCE"
          value = local.event_source
        },
        {
          name  = "NEW_RELIC_APP_NAME"
          value = "${local.new_relic_app_name}-App"
        },
        {
          name  = "NEW_RELIC_ENVIRONMENT"
          value = var.environment
        },

        {
          name  = "TASK_WORKER_QUEUE_URL"
          value = aws_sqs_queue.taskworker.url
        }
      ]
      essential = true
      portMappings = [
        {
          containerPort = 8000
        }
      ]

      LogConfiguration = {
        LogDriver = "awslogs"
        Options = {
          awslogs-region        = var.region
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-stream-prefix = local.service_name
        }
      }

      secrets = concat(local.new_relic_secrets, [
        {
          name      = "REDIS_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/${var.environment}/redis_auth_password"
        }
      ])

      # healthCheck = {
      #   command = [
      #     "CMD-SHELL",
      #     "curl -f http://localhost:8000/ping || exit 1"
      #   ]
      #   interval = 60
      #   retries = 3
      #   startPeriod = 60
      #   timeout = 5
      # }

    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  execution_role_arn = data.aws_iam_role.ecs-execution.arn
  task_role_arn      = aws_iam_role.sourcehub.arn

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-app"
  })
}

##
# DEPRECATED. Use aws_iam_role.sourcehub
##
resource "aws_iam_role" "app-task" {
  name = format("%s-%s-%s-app-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)

  assume_role_policy = jsonencode({
    Version = "2008-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  inline_policy {
    name = "ExecuteCommand"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "logs:CreateLogStream",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
            "logs:PutEvents"
          ]
          Resource = "*"
        },
        {
          Effect = "Allow"
          Action = [
            "ssmmessages:CreateControlChannel",
            "ssmmessages:OpenControlChannel",
            "ssmmessages:CreateDataChannel",
            "ssmmessages:OpenDataChannel"
          ]
          Resource = "*"
        },
        {
          Effect = "Allow"
          Action = [
            "s3:ListAllMyBuckets"
          ]
          Resource = "*"
        }
      ]
    })
  }

  managed_policy_arns = [
    data.aws_iam_policy.docrepo-contributor.arn,
    data.aws_iam_policy.sourcehub-eventbus-contributor.arn
  ]

  tags = merge(local.effective_tags, {
    Name      = format("%s-%s-%s-app-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)
    component = "${local.service_name}-app"
  })

}

resource "aws_security_group" "app" {
  name        = format("%s-%s-%s-app-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} SourceHub App Security Group"
  vpc_id      = data.aws_subnet.first-app-subnet.vpc_id

  ingress = [
    {
      description = "Allow HTTP from Load Balancer"
      from_port   = 80
      to_port     = 80
      protocol    = "TCP"
      security_groups = [
        data.aws_security_group.alb-public.id
      ]
      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      cidr_blocks      = null
      self             = false
    },
    {
      description = "Allow 8000 from Load Balancer"
      from_port   = 8000
      to_port     = 8000
      protocol    = "TCP"
      security_groups = [
        data.aws_security_group.alb-public.id
      ]
      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      cidr_blocks      = null
      self             = false
    }
  ]
  egress = [
    {
      description = "Allow ALL Outbound"
      from_port   = 0
      to_port     = 65535
      protocol    = "TCP"
      cidr_blocks = [
        "0.0.0.0/0"
      ]
      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      security_groups  = null
      self             = false
    }
  ]

  tags = merge(local.effective_tags, {
    Name      = format("%s-%s-%s-app-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-app"
  })

}

resource "aws_ecs_service" "app" {
  # Service Name should not include environment, since they are scoped to the Cluster which is scoped to an environment
  name             = "${local.service_name}-app"
  platform_version = "LATEST"
  cluster          = data.aws_ecs_cluster.ecs-cluster.id
  task_definition  = aws_ecs_task_definition.app.arn

  desired_count = 4
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  propagate_tags                     = "SERVICE"
  enable_execute_command             = true
  launch_type                        = "FARGATE"
  network_configuration {
    assign_public_ip = false
    subnets          = data.aws_subnets.app-subnet-ids.ids
    security_groups = [
      aws_security_group.app.id
    ]
  }
  health_check_grace_period_seconds = 60
  load_balancer {
    container_name   = "${local.service_name}-app"
    container_port   = 8000
    target_group_arn = aws_alb_target_group.app-http.arn
  }
  force_new_deployment = true

  depends_on = [
    null_resource.exec-dbmigrations
  ]
  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }
  tags = merge(local.effective_tags, {
    component = "${local.service_name}-app"
  })
}

resource "aws_alb_target_group" "app-http" {
  name = format("%s-%s-%s-http", local.app_name, var.environment, local.service_name)
  health_check {
    path    = "/ping"
    matcher = "200-299,303"
  }
  port                 = 80
  protocol             = "HTTP"
  deregistration_delay = 60

  target_type = "ip"
  vpc_id      = data.aws_subnet.first-app-subnet.vpc_id
  tags = {
    Name      = format("%s-%s-%s-http", local.app_name, var.environment, local.service_name)
    component = "${local.service_name}-app"
  }
}

resource "aws_alb_listener_rule" "app-https" {

  action {
    target_group_arn = aws_alb_target_group.app-http.arn
    type             = "forward"
  }
  condition {
    host_header {
      values = [
        local.dns_host
      ]
    }
  }
  priority = 10
  
  listener_arn = data.aws_lb_listener.https.arn

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-app"
  })

}
