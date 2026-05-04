# ─── EC2 Outputs ───────────────────────────────────────────
output "ec2_instance_id" {
  description = "ID de l'instance EC2 créée"
  value       = aws_instance.web_server.id
}

output "ec2_public_ip" {
  description = "Adresse IP publique de l'instance EC2"
  value       = aws_instance.web_server.public_ip
}

output "ec2_public_dns" {
  description = "DNS public de l'instance EC2"
  value       = aws_instance.web_server.public_dns
}

output "ec2_instance_type" {
  description = "Type d'instance EC2 utilisé"
  value       = aws_instance.web_server.instance_type
}

# ─── Security Group Outputs ────────────────────────────────
output "security_group_id" {
  description = "ID du Security Group créé"
  value       = aws_security_group.web_sg.id
}

output "security_group_name" {
  description = "Nom du Security Group"
  value       = aws_security_group.web_sg.name
}

# ─── S3 Outputs ────────────────────────────────────────────
output "s3_bucket_name" {
  description = "Nom du bucket S3 créé"
  value       = aws_s3_bucket.cloud_ia_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3"
  value       = aws_s3_bucket.cloud_ia_bucket.arn
}

# ─── Récapitulatif ─────────────────────────────────────────
output "deployment_summary" {
  description = "Résumé complet du déploiement"
  value = {
    instance_id   = aws_instance.web_server.id
    public_ip     = aws_instance.web_server.public_ip
    bucket_name   = aws_s3_bucket.cloud_ia_bucket.id
    security_group = aws_security_group.web_sg.id
    region        = var.aws_region
    environment   = var.environment_tag
  }
}
