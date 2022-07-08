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


resource "aws_cloudwatch_log_group" "sourcehub-events" {
  name = "/aws/events/sourcehub"
  retention_in_days = 30
}

data "aws_iam_policy_document" "sourcehub-events-log-policy" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.sourcehub-events.arn}"
    ]

    principals {
      identifiers = [
        "events.amazonaws.com", 
        "delivery.logs.amazonaws.com"
      ]
      type        = "Service"
    }

    condition {
      test     = "ArnEquals"
      values   = [
        aws_cloudwatch_event_rule.sourcehub-events.arn
      ]
      variable = "aws:SourceArn"
    }
  }
}
resource "aws_cloudwatch_log_resource_policy" "sourcehub-events-log-policy" {
  policy_name = "sourcehub-events-log-policy"
  policy_document = data.aws_iam_policy_document.sourcehub-events-log-policy.json
}

resource "aws_cloudwatch_event_rule" "sourcehub-events" {
  name = "sourcehub-events-log"
  description = "Log SourceHub Events to CloudWatch Logs"

  event_bus_name = aws_cloudwatch_event_bus.sourcehub.name
  is_enabled = true

  event_pattern = jsonencode(
    {
      "source": [
        local.event_source
      ]
    }
  )
  
  tags = merge(local.effective_tags, {
    Name = "sourcehub-events-log"
  })
}

resource "aws_cloudwatch_event_target" "sourcehub-events-log" {
  rule           = aws_cloudwatch_event_rule.sourcehub-events.name
  arn            = aws_cloudwatch_log_group.sourcehub-events.arn
  event_bus_name = aws_cloudwatch_event_bus.sourcehub.name
  
}