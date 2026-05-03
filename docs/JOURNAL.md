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
