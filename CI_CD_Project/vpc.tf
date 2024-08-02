
resource "aws_vpc" "test_vpc" {
  assign_generated_ipv6_cidr_block     = false
  cidr_block                           = "172.31.0.0/16"
  enable_dns_hostnames                 = true
  enable_dns_support                   = true
  enable_network_address_usage_metrics = false
  ipv6_netmask_length                  = 0
  tags                                 = {}
  tags_all                             = {}
}
