resource "aws_cloudwatch_log_group" "scrapeworker" {
  name = format("/%s/%s-%s-scrapeworker", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30
  
  tags = merge(local.effective_tags, {
    component = "${local.service_name}-scrapeworker"
  })
}

resource "aws_ecs_task_definition" "scrapeworker" {
  family                   = "${local.service_name}-scrapeworker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  # TODO: Make cpu, memory a variable and determine appropriate thresholds
  cpu                      = 1024
  memory                   = 2048
  

  container_definitions = jsonencode([
    {
      name  = "${local.service_name}-app"
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-scrapeworker-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && python scrapeworker/main.py"
      ]
      environment = [
        {
          name = "ENV_TYPE"
          value = var.environment
        },
        {
          name = "S3_ENDPOINT_URL"
          value = data.aws_service.s3.dns_name
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
          awslogs-region = var.region
          awslogs-group = aws_cloudwatch_log_group.scrapeworker.name
          awslogs-stream-prefix = local.service_name
        }
      }

      secrets = [
        {
          name = "MONGO_URL"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/mongodb_url"
        },
        {
          name = "MONGO_DB"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/mongodb_db"
        },
        {
          name = "MONGO_USER"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/mongodb_user"
        },
        {
          name = "MONGO_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/mongodb_password"
        },
        {
          name = "REDIS_URL"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/redis_url"
        },
        {
          name = "REDIS_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/redis_auth_password"
        },
        {
          name = "S3_DOCUMENT_BUCKET"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/docrepo_bucket_name"
        }
      ]

    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  execution_role_arn = data.aws_iam_role.ecs-execution.arn
  task_role_arn      = aws_iam_role.scrapeworker-task.arn

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-scrapeworker"
  })
}

resource "aws_iam_role" "scrapeworker-task" {
  name = format("%s-%s-%s-scrapeworker-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)

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
        }
      ]
    })
  }

  managed_policy_arns = [
    data.aws_iam_policy.docrepo-contributor.arn
  ]

  tags = merge(local.effective_tags, {
    Name = format("%s-%s-%s-scrapeworker-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)
    component = "${local.service_name}-scrapeworker"
  })

}

resource "aws_security_group" "scrapeworker" {
  name        = format("%s-%s-%s-scrapeworker-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} Scrape Worker Security Group"
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
    Name = format("%s-%s-%s-scrapeworker-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-scrapeworker"
  })
}

resource "aws_ecs_service" "scrapeworker" {
  name             = "${local.service_name}-scrapeworker"
  platform_version = "LATEST"
  cluster          = data.aws_ecs_cluster.ecs-cluster.id
  task_definition  = aws_ecs_task_definition.scrapeworker.arn
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
      aws_security_group.scrapeworker.id
    ]
  }
  force_new_deployment = true
}