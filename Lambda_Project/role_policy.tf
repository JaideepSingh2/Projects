
resource "aws_iam_policy" "administrator" {
  description = null
  name        = "start-stop_instances"
  name_prefix = null
  path        = "/"
  policy = jsonencode({
    Statement = [{
      Action   = ["ec2:StartInstances", "ec2:StopInstances"]
      Effect   = "Allow"
      Resource = "*"
      Sid      = "VisualEditor0"
    }]
    Version = "2012-10-17"
  })
  tags     = {}
  tags_all = {}
}
