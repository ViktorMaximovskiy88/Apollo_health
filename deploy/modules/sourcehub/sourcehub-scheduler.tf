resource "aws_cloudwatch_log_group" "scheduler" {
  name = format("/%s/%s-%s-scheduler", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-scheduler"
  })
}

resource "aws_ecs_task_definition" "scheduler" {
  family                   = "${local.service_name}-scheduler-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  # TODO: Make cpu, memory a variable and determine appropriate thresholds
  cpu    = 1024
  memory = 2048


  container_definitions = jsonencode([
    {
      name  = "${local.service_name}-app"
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-scheduler-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && exec python scheduler/main.py"
      ]
      environment = [
        {
          name  = "ENV_TYPE"
          value = var.environment
        },
        {
          name  = "PYTHONUNBUFFERED"
          value = "1"
        },
        {
          name  = "S3_ENDPOINT_URL"
          value = data.aws_service.s3.dns_name
        },
        {
          name  = "CLUSTER_ARN"
          value = data.aws_ecs_cluster.ecs-cluster.arn
        },
        {
          name  = "SCRAPEWORKER_SERVICE_ARN"
          value = aws_ecs_service.scrapeworker.id
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
          name  = "NEW_RELIC_APP_NAME"
          value = "${local.new_relic_app_name}-Scheduler"
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
          awslogs-group         = aws_cloudwatch_log_group.scheduler.name
          awslogs-stream-prefix = local.service_name
        }
      }

      secrets = concat(local.new_relic_secrets, [
        {
          name      = "REDIS_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/${var.environment}/redis_auth_password"
        }
      ])
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  execution_role_arn = data.aws_iam_role.ecs-execution.arn
  task_role_arn      = aws_iam_role.sourcehub.arn

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-scheduler"
  })
}

##
# DEPRECATED. Use aws_iam_role.sourcehub
##
resource "aws_iam_role" "scheduler-task" {
  name = format("%s-%s-%s-scheduler-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)

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
        },
        {
          Effect = "Allow"
          Action = [
            "ecs:DescribeClusters"
          ]
          Resource = [
            data.aws_ecs_cluster.ecs-cluster.arn
          ]
        },
        {
          Effect = "Allow"
          Action = [
            "ecs:DescribeServices",
            "ecs:UpdateService"
          ]
          Resource = [
            aws_ecs_service.scrapeworker.id
          ]
        },
        {
          Action = [
            "ecs:ListTasks",
            "ecs:DescribeTasks",
            "ecs:StopTask"
          ]
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }

  managed_policy_arns = [
    data.aws_iam_policy.docrepo-contributor.arn
  ]

  tags = merge(local.effective_tags, {
    Name      = format("%s-%s-%s-scheduler-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)
    component = "${local.service_name}-scheduler"
  })

}

resource "aws_security_group" "scheduler" {
  name        = format("%s-%s-%s-scheduler-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} Scheduler Security Group"
  vpc_id      = data.aws_subnet.first-app-subnet.vpc_id

  ingress = [

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
    Name      = format("%s-%s-%s-scheduler-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-scheduler"
  })
}

resource "aws_ecs_service" "scheduler" {
  # Service Name should not include environment, since they are scoped to the Cluster which is scoped to an environment
  name             = "${local.service_name}-scheduler"
  platform_version = "LATEST"
  cluster          = data.aws_ecs_cluster.ecs-cluster.id
  task_definition  = aws_ecs_task_definition.scheduler.arn
  desired_count    = 1
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
      aws_security_group.scheduler.id
    ]
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
    component = "${local.service_name}-scheduler"
  })
}
