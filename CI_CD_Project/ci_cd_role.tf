resource "aws_iam_role" "ci_cd_role" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "codepipeline.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
  description           = null
  force_detach_policies = false
  managed_policy_arns   = ["arn:aws:iam::975050352921:policy/service-role/AWSCodePipelineServiceRole-us-east-1-Newpipe"]
  max_session_duration  = 3600
  name                  = "AWSCodePipelineServiceRole-us-east-1-Newpipe"
  name_prefix           = null
  path                  = "/service-role/"
  permissions_boundary  = null
  tags                  = {}
  tags_all              = {}
}
