# ─── Région AWS ────────────────────────────────────────────
variable "aws_region" {
  description = "Région AWS où déployer l'infrastructure"
  type        = string
  default     = "eu-west-3"
}

# ─── Credentials AWS ───────────────────────────────────────
variable "aws_access_key" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

# ─── EC2 ───────────────────────────────────────────────────
variable "instance_type" {
  description = "Type d'instance EC2 (Free Tier : t2.micro)"
  type        = string
  default     = "t3.micro"
}

variable "instance_name" {
  description = "Nom de l'instance EC2"
  type        = string
  default     = "cloud-ia-web-server"
}

variable "ami_id" {
  description = "AMI Ubuntu 22.04 LTS pour eu-west-3 (Paris)"
  type        = string
  default     = "ami-02aabe2c1c59b6feb"
}

# ─── S3 ────────────────────────────────────────────────────
variable "bucket_name" {
  description = "Nom unique du bucket S3 (doit être unique globalement)"
  type        = string
  default     = "cloud-ia-bucket-2026"
}

# ─── SSH ───────────────────────────────────────────────────
variable "key_pair_name" {
  description = "Nom de la clé SSH pour accéder à l'EC2"
  type        = string
  default     = "cloud-ia-key"
}

# ─── Tags ──────────────────────────────────────────────────
variable "project_tag" {
  description = "Tag projet appliqué à toutes les ressources"
  type        = string
  default     = "cloud-ia-agent"
}

variable "environment_tag" {
  description = "Tag environnement"
  type        = string
  default     = "dev"
}
