resource "aws_cloudwatch_log_group" "pdfdiffworker" {
  name = format("/%s/%s-%s-pdfdiffworker", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-pdfdiffworker"
  })
}

resource "aws_ecs_task_definition" "pdfdiffworker" {
  family                   = "${local.service_name}-pdfdiffworker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  # TODO: Make cpu, memory a variable and determine appropriate thresholds
  cpu    = 1024
  memory = 2048


  container_definitions = jsonencode([
    {
      name  = "${local.service_name}-app"
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-pdfdiffworker-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && python pdfdiffworker/main.py"
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
          value = "${local.new_relic_app_name}-pdfdiffworker"
        },
        {
          name = "PDFDIFF_WORKER_QUEUE_URL"
          value = aws_sqs_queue.pdfdiffworker.url
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
          awslogs-group         = aws_cloudwatch_log_group.pdfdiffworker.name
          awslogs-stream-prefix = local.service_name
        }
      }

      secrets = concat(local.new_relic_secrets, [
        {
          name      = "REDIS_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/redis_auth_password"
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
    component = "${local.service_name}-pdfdiffworker"
  })
}

resource "aws_security_group" "pdfdiffworker" {
  name        = format("%s-%s-%s-pdfdiffworker-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} Lineage Worker Security Group"
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
    Name      = format("%s-%s-%s-pdfdiffworker-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-pdfdiffworker"
  })
}

resource "aws_ecs_service" "pdfdiffworker" {
  name             = "${local.service_name}-pdfdiffworker"
  platform_version = "LATEST"
  cluster          = data.aws_ecs_cluster.ecs-cluster.id
  task_definition  = aws_ecs_task_definition.pdfdiffworker.arn
  desired_count    = 0
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
      aws_security_group.pdfdiffworker.id
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
    component = "${local.service_name}-pdfdiffworker"
  })
}


resource "aws_sqs_queue" "pdfdiffworker" {
  name = format("%s-%s-%s-pdfdiffworker-%s-mmit-sqs-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)

  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600 # 4 days
  delay_seconds              = 0

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-pdfdiffworker"
  })
}

resource "aws_appautoscaling_target" "pdfdiffworker" {
  max_capacity       = 3
  min_capacity       = 0
  resource_id        = "service/${data.aws_ecs_cluster.ecs-cluster.cluster_name}/${local.service_name}-pdfdiffworker"
  role_arn           = aws_iam_service_linked_role.autoscaling.arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "pdfdiffworker_scale_up" {
  policy_type        = "StepScaling"
  name               = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-up"
  resource_id        = aws_appautoscaling_target.pdfdiffworker.resource_id
  scalable_dimension = aws_appautoscaling_target.pdfdiffworker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.pdfdiffworker.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ExactCapacity"
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 10
      scaling_adjustment          = 1
    }
    step_adjustment {
      metric_interval_lower_bound = 10
      metric_interval_upper_bound = 20
      scaling_adjustment          = 2
    }
    step_adjustment {
      metric_interval_lower_bound = 20
      scaling_adjustment          = 3
    }
  }
}

resource "aws_appautoscaling_policy" "pdfdiffworker_scale_down" {
  policy_type        = "StepScaling"
  name               = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-down"
  resource_id        = aws_appautoscaling_target.pdfdiffworker.resource_id
  scalable_dimension = aws_appautoscaling_target.pdfdiffworker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.pdfdiffworker.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ExactCapacity"
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = 0
    }

  }
}

resource "aws_cloudwatch_metric_alarm" "pdfdiffworker_scale_up" {
  alarm_name = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-up-alarm"

  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = "60"
  threshold                 = "1"
  statistic                 = "Sum"
  alarm_description         = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-up-alarm"
  insufficient_data_actions = []
  alarm_actions = [
    aws_appautoscaling_policy.pdfdiffworker_scale_up.arn
  ]

  dimensions = {
    QueueName = aws_sqs_queue.pdfdiffworker.name
  }
}

resource "aws_cloudwatch_metric_alarm" "pdfdiffworker_scale_down" {
  alarm_name = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-down-alarm"

  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  threshold           = "1"
  statistic           = "Sum"
  alarm_description   = "${local.app_name}-${local.service_name}-pdfdiffworker-sqs-scale-down-alarm"
  alarm_actions = [
    aws_appautoscaling_policy.pdfdiffworker_scale_down.arn
  ]


  dimensions = {
    QueueName = aws_sqs_queue.pdfdiffworker.name
  }
}
