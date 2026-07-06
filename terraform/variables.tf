variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Name prefix used for tagging resources"
  type        = string
  default     = "aiops-watcher"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type (keep free-tier eligible)"
  type        = string
  default     = "m7i-flex.large"
}

variable "my_ip" {
  description = "Your public IP in CIDR notation, e.g. 123.45.67.89/32 (used to restrict SSH)"
  type        = string
}

variable "key_pair_name" {
  description = "Name of the existing EC2 key pair to use for SSH access"
  type        = string
}
