resource "aws_cloudwatch_log_group" "dbmigrations" {
  name = format("/%s/%s-%s-dbmigrations", local.app_name, var.environment, local.service_name)
  # TODO: Make this a variable and determine appropriate threshold
  retention_in_days = 30
  
  tags = merge(local.effective_tags, {
    component = "${local.service_name}-dbmigrations"
  })
}

resource "aws_ecs_task_definition" "dbmigrations" {
  family                   = "${local.service_name}-dbmigrations"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512 # 0.5 vCPU
  memory                   = 1024
  

  container_definitions = jsonencode([
    {
      name  = "${local.service_name}-app"
      image = "${data.aws_ecr_repository.sourcehub-app.repository_url}:${var.sourcehub-dbmigrations-version}"
      command = [
        "/bin/bash",
        "-lc",
        ". ./venv/bin/activate && exec python common/db/migrations.py"
      ]
      environment = [
        {
          name = "ENV_TYPE"
          value = var.environment
        },
        {
          name = "PYTHONUNBUFFERED"
          value = "1"
        },
        {
          name = "S3_ENDPOINT_URL"
          value = data.aws_service.s3.dns_name
        },
        {
          name = "MONGO_URL"
          value = local.mongodb_url
        },
        {
          name = "MONGO_DB"
          value = local.mongodb_db
        },
         {
          name = "REDIS_URL"
          value = data.aws_ssm_parameter.redis-url.value
        },
        {
          name = "S3_DOCUMENT_BUCKET"
          value = data.aws_ssm_parameter.docrepo-bucket-name.value
        },
        {
          name = "SMARTPROXY_USERNAME"
          value = data.aws_ssm_parameter.smartproxy-username.value
        }
      ]
      essential = true

      LogConfiguration = {
        LogDriver = "awslogs"
        Options = {
          awslogs-region = var.region
          awslogs-group = aws_cloudwatch_log_group.dbmigrations.name
          awslogs-stream-prefix = local.service_name
        }
      }

      secrets = [
        {
          name = "REDIS_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/redis_auth_password"
        },
        {
          name = "SMARTPROXY_PASSWORD"
          valueFrom = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/apollo/smartproxy_password"
        }
      ]

    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  execution_role_arn = data.aws_iam_role.ecs-execution.arn
  task_role_arn      = aws_iam_role.sourcehub.arn

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-dbmigrations"
  })
}

resource "aws_iam_role" "dbmigrations-task" {
  name = format("%s-%s-%s-dbmigrations-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)

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
  ]

  tags = merge(local.effective_tags, {
    Name = format("%s-%s-%s-dbmigrations-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)
    component = "${local.service_name}-dbmigrations"
  })

}

resource "aws_security_group" "dbmigrations" {
  name        = format("%s-%s-%s-dbmigrations-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
  description = "${title(local.app_name)} DB Migrations Security Group"
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
    Name = format("%s-%s-%s-dbmigrations-%s-mmit-sg-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision)
    component = "${local.service_name}-dbmigrations"
  })
}

locals {
  network_configuration = {
    awsvpcConfiguration = {
      assignPublicIp = "DISABLED"
      subnets          = data.aws_subnets.app-subnet-ids.ids
      securityGroups = [
        aws_security_group.dbmigrations.id
      ]
    }
  }

}

resource "null_resource" "exec-dbmigrations" {
  depends_on = [
    aws_ecs_task_definition.dbmigrations
  ]
  triggers = {
    task_definition_arn = aws_ecs_task_definition.dbmigrations.arn
  }
  provisioner "local-exec" {
    interpreter = [
      "/bin/bash", "-c"
    ]
    command = <<EOF
set -e

# Initialize variables used in script
CLUSTER=${data.aws_ecs_cluster.ecs-cluster.id}
TASK_DEF=${aws_ecs_task_definition.dbmigrations.family}:${aws_ecs_task_definition.dbmigrations.revision}
NETWORK_CONFIG='${jsonencode(local.network_configuration)}'

# Run DB Migration Task
TASK_ARN=$(aws ecs run-task \
  --cluster $CLUSTER \
  --task-definition $TASK_DEF \
  --launch-type FARGATE \
  --network-configuration $NETWORK_CONFIG \
  --query '(tasks[].taskArn)[0]' \
  --output text)


# Wait until Task moves to Stopped state, checking every 6 seconds
aws ecs wait tasks-stopped \
  --cluster $CLUSTER \
  --tasks $TASK_ARN

# Get Exit Code
TASK_EXIT_CODE=$(aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks $TASK_ARN \
  --query "tasks[0].containers[0].exitCode" \
  --output text)

exit $TASK_EXIT_CODE
EOF
  }
}