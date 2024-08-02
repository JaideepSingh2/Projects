
resource "aws_instance" "my_instance" {
  ami           = "ami-04a81a99f5ec58529"
  instance_type = "t2.micro"
  key_name      = ""
  vpc_security_group_ids = ["sg-0c6441dd4faf0c8dc"]
  subnet_id     = ""

  root_block_device {
    volume_type = "gp3"
    volume_size = 8
  }

  tags = {
    Name = "My instance"
  }
}