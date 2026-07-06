output "vm_public_ip" {
  description = "Public (Elastic) IP of the VM"
  value       = aws_eip.vm.public_ip
}

output "vm_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.vm.id
}

output "ssh_command" {
  description = "Convenience SSH command"
  value       = "ssh -i <path-to-your-key.pem> ubuntu@${aws_eip.vm.public_ip}"
}
