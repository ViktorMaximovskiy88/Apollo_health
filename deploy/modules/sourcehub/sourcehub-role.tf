resource "aws_iam_role" "sourcehub" {
  name = format("%s-%s-%s-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)

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
            "arn:aws:ecs:${var.region}:${data.aws_caller_identity.current.account_id}:service/${data.aws_ecs_cluster.ecs-cluster.cluster_name}/${local.service_name}-scrapeworker"
          ]
        }
      ]
    })
  }

  managed_policy_arns = [
    data.aws_iam_policy.docrepo-contributor.arn,
    data.aws_iam_policy.sourcehub-eventbus-contributor.arn
  ]

  tags = merge(local.effective_tags, {
    Name = format("%s-%s-%s-app-mmit-role-%02d", local.app_name, var.environment, local.service_name, var.revision)
    component = "${local.service_name}-app"
  })

}