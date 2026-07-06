resource "aws_instance" "vm" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.vm.id]
  key_name               = var.key_pair_name

  root_block_device {
    volume_size = 20 # GB, within free-tier limit (30GB/month)
    volume_type = "gp3"
  }

  tags = {
    Name = "${var.project_name}-vm"
  }
}

resource "aws_eip" "vm" {
  instance = aws_instance.vm.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }
}
