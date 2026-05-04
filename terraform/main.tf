# ─── Provider AWS ──────────────────────────────────────────
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# ─── Data : récupère le VPC par défaut ─────────────────────
data "aws_vpc" "default" {
  default = true
}

# ─── Security Group ────────────────────────────────────────
resource "aws_security_group" "web_sg" {
  name        = "cloud-ia-web-sg"
  description = "Security Group pour le serveur web cloud-ia-agent"
  vpc_id      = data.aws_vpc.default.id

  # HTTP entrant
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS entrant
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH entrant (pour administration)
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Tout sortant autorisé
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "cloud-ia-web-sg"
    Project     = var.project_tag
    Environment = var.environment_tag
  }
}

# ─── Clé SSH ───────────────────────────────────────────────
resource "aws_key_pair" "cloud_ia_key" {
  key_name   = var.key_pair_name
  public_key = file("${path.module}/../cloud-ia-key.pub")

  tags = {
    Project     = var.project_tag
    Environment = var.environment_tag
  }
}

# ─── Instance EC2 t2.micro (Free Tier) ─────────────────────
resource "aws_instance" "web_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.cloud_ia_key.key_name
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # Script de démarrage automatique
  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    echo "<h1>Cloud IA Agent - Deployed by Terraform</h1>" \
      > /var/www/html/index.html
  EOF

  tags = {
    Name        = var.instance_name
    Project     = var.project_tag
    Environment = var.environment_tag
  }
}

# ─── Bucket S3 (Free Tier : 5 Go gratuits) ─────────────────
resource "aws_s3_bucket" "cloud_ia_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Name        = var.bucket_name
    Project     = var.project_tag
    Environment = var.environment_tag
  }
}

# Bloquer tout accès public au bucket (bonne pratique sécurité)
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.cloud_ia_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning du bucket activé
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.cloud_ia_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
