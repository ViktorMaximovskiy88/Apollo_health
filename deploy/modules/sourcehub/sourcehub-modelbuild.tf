resource "aws_cloudwatch_log_group" "modelbuild" {
  name = format("/%s/%s-%s-modelbuild", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-modelbuild"
  })
}

resource "aws_ecs_task_definition" "modelbuild" {
  family                   = "${local.service_name}-modelbuild-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  # TODO: Make cpu, memory a variable and determine appropriate thresholds
  cpu    = 4096
  memory = 8192


  container_definitions = jsonencode([
    {
      name = "${local.service_name}-app"
      ##
      # Will use parseworker-version and NOT define a new version var for modelbuild
      ##
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-parseworker-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && python parseworker/scripts/process_tagging_models.py"
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
          name  = "EVENT_BUS_ARN"
          value = data.aws_cloudwatch_event_bus.sourcehub.arn
        },
        {
          name  = "EVENT_SOURCE"
          value = local.event_source
        },
        {
          name  = "NEW_RELIC_APP_NAME"
          value = "${local.new_relic_app_name}-ModelBuild"
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
          awslogs-group         = aws_cloudwatch_log_group.modelbuild.name
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
    component = "${local.service_name}-modelbuild"
  })
}

resource "aws_security_group" "modelbuild" {
  name        = format("%s-%s-%s-modelbuild-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} Model Build Security Group"
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
    Name      = format("%s-%s-%s-modelbuild-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-modelbuild"
  })
}

resource "aws_scheduler_schedule" "modelbuild" {
  name       = "sourcehub-modelbuild-${var.environment}"
  group_name = "default"

  state = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(30 2 * * ? *)"
  schedule_expression_timezone = "UTC"

  target {
    arn      = data.aws_ecs_cluster.cluster.arn
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.modelbuild.arn
      launch_type         = "FARGATE"
      task_count          = 1
      network_configuration {
        assign_public_ip = false
        subnets          = data.aws_subnets.app-subnet-ids.ids
        security_groups = [
          aws_security_group.modelbuild.id
        ]
      }
    }
  }
}
