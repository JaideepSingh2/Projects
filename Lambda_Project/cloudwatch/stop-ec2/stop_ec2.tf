
resource "aws_cloudwatch_event_rule" "console" {
  description         = null
  event_bus_name      = "default"
  event_pattern       = null
  force_destroy       = false
  name                = "stopec2"
  name_prefix         = null
  role_arn            = null
  schedule_expression = "cron(05 20 ? * 4 *)"
  state               = "ENABLED"
  tags                = {}
  tags_all            = {}
}
