
resource "aws_db_instance" "database-1" {
  allocated_storage                     = 20
  auto_minor_version_upgrade            = true
  availability_zone                     = "us-east-1a"
  db_name                               = "agms"
  db_subnet_group_name                  = "default-vpc-01560b4d9a9708490"
  deletion_protection                   = false
  enabled_cloudwatch_logs_exports       = []
  engine                                = "mysql"
  engine_version                        = "8.0.35"
  identifier                            = "database-1"
  instance_class                        = "db.t3.micro"
  iops                                  = 0
  max_allocated_storage                 = 1000
  monitoring_interval                   = 0
  monitoring_role_arn                   = null
  password                              = "mysql-123"
  performance_insights_enabled          = false
  port                                  = 3306
  publicly_accessible                   = true
  storage_encrypted                     = true
  storage_type                          = "gp2"
  tags                                  = {}
  tags_all                              = {}
  username                              = "root"
  vpc_security_group_ids                = ["sg-0c6441dd4faf0c8dc"]
}
