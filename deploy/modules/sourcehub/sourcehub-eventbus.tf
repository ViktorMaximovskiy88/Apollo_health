resource "aws_cloudwatch_event_bus" "sourcehub" {
  name = format("%s-%s-%s-mmit-bus-%02d", local.app_name, var.environment,  local.service_name, var.revision)

  tags = merge(local.effective_tags, {
    component = "${local.service_name}-eventbus"
  })
}

resource "aws_iam_policy" "sourcehub-eventbus-contributor" {
  name        = format("%s-%s-%s-eventbus-contributor-mmit-policy-%02d", local.app_name, var.environment, local.service_name, var.revision)
  path        = "/"
  description = "Provide Write access to SourceHub Event Bus when Event Source is from SourceHub"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "events:PutEvents"
        ],
        Resource = [
          aws_cloudwatch_event_bus.sourcehub.arn
        ],
        Condition = {
          StringEquals = {
            "events:source"= local.event_source
          }
        }
      }
    ]
  })

  tags = merge(local.effective_tags, {})
}