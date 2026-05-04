# Journal de bord — Cloud IA Agent

## Jour 1 — Configuration de l'environnement
**Date :** $(date +%Y-%m-%d)

### Réalisé
- Installation Ubuntu 24.04 sur VMware
- Python 3.12, pip, venv configurés
- Terraform installé et fonctionnel
- AWS CLI v2 configuré
- Ollama + modèle Mistral opérationnels
- Structure du projet créée
- Repo GitHub initialisé


### Décisions techniques
- LLM local : Ollama + Mistral
- Region AWS : eu-west-3 (Paris)
- Instance : t2.micro 


## Jour 2 — Agent Python IA + boto3
**Date :** 2026-XX-XX

### Réalisé
- ia_agent.py : agent Ollama/Mistral avec prompt système structuré
- aws_analyzer.py : inventaire EC2, S3, Security Groups via boto3
- main.py : CLI complète agent → inventaire → suggestion architecture
- tests/test_agent.py : 8 tests unitaires avec mocks, tous passent
- pytest installé et fonctionnel

### Décisions techniques
- Réponse Mistral parsée en JSON avec extraction robuste (find/rfind)
- Mocks boto3 pour les tests (pas d'appels AWS réels pendant les tests)
- Timeout Ollama fixé à 120s pour les machines lentes

## Jour 3 — Scripts Terraform
**Date :** 2026-XX-XX

### Réalisé
- variables.tf : toutes les variables paramétrables centralisées
- main.tf : EC2 t2.micro + Security Group (HTTP/HTTPS/SSH) + S3 bucket
- outputs.tf : IP publique, ID instance, ARN bucket, résumé déploiement
- terraform.tfvars : valeurs sensibles (dans .gitignore)
- Clé SSH générée pour l'accès EC2
- terraform init : provider AWS 5.x téléchargé
- terraform validate : configuration valide
- terraform plan : 6 ressources prêtes à déployer

### Décisions techniques
- AMI Ubuntu 22.04 LTS (ami-0f15d55736fd476da) pour eu-west-3
- force_destroy=true sur S3 pour faciliter le terraform destroy
- Versioning S3 activé dès le départ
- Accès public S3 bloqué par défaut (sécurité)
- user_data installe nginx automatiquement au démarrage EC2
