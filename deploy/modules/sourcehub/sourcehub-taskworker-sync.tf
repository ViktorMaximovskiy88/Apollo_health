locals {
  function_name = format("%s-%s-%s-%s-%s-mmit-func-%02d", local.app_name, var.environment, local.service_name, local.short_region, "taskworker-sync", var.revision)
}

resource "aws_lambda_function" "sourcehub-taskworker-sync" {
  function_name = local.function_name
  role          = aws_iam_role.sourcehub-taskworker-sync-function.arn
  image_uri     = "${data.aws_ecr_repository.sourcehub-taskworker-sync.repository_url}:${var.sourcehub-taskworker-version}"

  package_type = "Image"
  timeout      = 60 # seconds

  environment {
    variables = {
      ENV_TYPE              = var.environment
      MONGO_URL             = local.mongodb_url
      MONGO_DB              = local.mongodb_db
      TASK_WORKER_QUEUE_URL = aws_sqs_queue.taskworker.url
      REDIS_URL             = data.aws_ssm_parameter.redis-url.value
      S3_ENDPOINT_URL       = data.aws_service.s3.dns_name
      S3_DOCUMENT_BUCKET    = data.aws_ssm_parameter.docrepo-bucket-name.value
      SMARTPROXY_USERNAME   = data.aws_ssm_parameter.smartproxy-username.value
    }
  }

  architectures = [
    "x86_64"
  ]

  tags = merge(local.effective_tags, {
    Name = local.function_name
  })
}

resource "aws_iam_role" "sourcehub-taskworker-sync-function" {
  name = format("%s-%s-%s-%s-%s-mmit-role-%02d", local.app_name, var.environment, local.service_name, local.short_region, "taskworker-sync", var.revision)

  assume_role_policy = jsonencode({
    Version = "2008-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  managed_policy_arns = [
    data.aws_iam_policy.secrets-reader.arn,
    data.aws_iam_policy.params-reader.arn,
    aws_iam_policy.sourcehub-taskworker-sync-function-basic.arn
  ]

  tags = merge(local.effective_tags, {
    Name = format("%s-%s-%s-%s-mmit-role-%02d", local.app_name, var.environment, local.service_name, local.short_region, var.revision),
    role = "sourcehub-taskworker-sync-function"
  })
}

resource "aws_iam_policy" "sourcehub-taskworker-sync-function-basic" {
  name        = format("%s-%s-%s-func-basic-mmit-policy-%02d", local.app_name, var.environment, local.service_name, var.revision)
  path        = "/"
  description = "Basic Execution Policy for SourceHub TaskworkerSync Function"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup"
        ],
        Resource = [
          "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = [
          "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.function_name}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes",
          "sqs:DeleteMessage",
          "sqs:ChangeMessageVisibility"
        ],
        Resource = [
          aws_sqs_queue.taskworker.arn,
          aws_sqs_queue.taskworker_dlq.arn,
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ],
        Resource = [
          data.aws_ecr_repository.sourcehub-taskworker-sync.arn
        ]
      },
    ]
  })

  tags = merge(local.effective_tags, {
    Name = format("%s-%s-%s-func-basic-mmit-policy-%02d", local.app_name, var.environment, local.service_name, var.revision)
  })
}

resource "aws_lambda_event_source_mapping" "sourcehub-taskworker-trigger" {
  event_source_arn = aws_sqs_queue.taskworker_dlq.arn
  enabled          = true
  function_name    = local.function_name
  batch_size       = 1

  depends_on = [
    aws_lambda_function.sourcehub-taskworker-sync
  ]
}
