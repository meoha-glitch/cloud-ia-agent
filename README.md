# Cloud IA Agent — Déploiement AWS piloté par IA

> Agent Python intelligent qui analyse un besoin utilisateur,
> suggère une architecture AWS via un LLM local (Ollama/Mistral),
> et provisionne l'infrastructure automatiquement via Terraform.

---

## Stack technique

| Outil | Rôle | Coût |
|---|---|---|
| Python 3.12 | Langage principal | Gratuit |
| Ollama + Mistral 7B | LLM local pour suggestion d'architecture | Gratuit |
| Terraform | Provisionnement infrastructure AWS | Gratuit |
| boto3 | Inventaire et interaction AWS | Gratuit |
| AWS Free Tier | Hébergement EC2 + S3 | Gratuit |
| pytest | Tests unitaires | Gratuit |

---

## Architecture du système
Utilisateur
│
▼
main.py (CLI interactive)
│
├── agent/ia_agent.py
│       └── Ollama/Mistral (LLM local)
│               └── Suggestion architecture JSON
│
├── agent/aws_analyzer.py
│       └── boto3 → AWS API
│               └── Inventaire EC2, S3, SG
│
└── terraform/
├── main.tf       (EC2 + S3 + Security Group)
├── variables.tf  (paramètres)
└── outputs.tf    (IP, ARN, résumé)


---

## Infrastructure déployée sur AWS

| Ressource | Type | Free Tier |
|---|---|---|
| EC2 Instance | t3.micro Ubuntu 22.04 | ✅ 750h/mois |
| S3 Bucket | Standard + versioning | ✅ 5 Go |
| Security Group | HTTP + HTTPS + SSH | ✅ Gratuit |
| Key Pair SSH | RSA 4096 bits | ✅ Gratuit |

---

## Prérequis

- Ubuntu 24.04 (VM VMware recommandée)
- Python 3.12+
- Terraform >= 1.5
- AWS CLI v2
- Ollama installé avec le modèle Mistral
- Compte AWS Free Tier

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/TON_USERNAME/cloud-ia-agent.git
cd cloud-ia-agent
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Installer Ollama et Mistral

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
ollama serve &
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
nano .env
```

Remplis avec tes clés AWS :

```env
AWS_ACCESS_KEY_ID=ta_cle_ici
AWS_SECRET_ACCESS_KEY=ton_secret_ici
AWS_DEFAULT_REGION=eu-west-3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 5. Configurer Terraform

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars
```

---

## Utilisation

```bash
python main.py
```

Menu interactif :

[1] Analyser mon compte AWS (inventaire boto3)
[2] Suggérer une architecture via IA (Ollama)
[3] Déployer l'infrastructure (terraform apply)
[4] Détruire l'infrastructure (terraform destroy)
[5] Voir les outputs du dernier déploiement
[6] Cycle complet (IA + init + validate + plan + apply)
[0] Quitter

---

## Cycle DevOps complet

```bash
# Dans le dossier terraform/
terraform init      # Télécharge le provider AWS
terraform validate  # Vérifie la syntaxe
terraform plan      # Prévisualise les changements
terraform apply     # Déploie sur AWS
terraform destroy   # Supprime toutes les ressources
```

---

## Tests

```bash
pytest tests/test_agent.py -v
```

16 tests unitaires couvrant :
- Agent IA (Ollama/Mistral) avec mocks
- Analyseur AWS (boto3) avec mocks
- Orchestration Terraform (subprocess)

---

## Structure du projet

cloud-ia-agent/
├── agent/
│   ├── ia_agent.py        # Agent Ollama/Mistral
│   └── aws_analyzer.py    # Inventaire boto3
├── terraform/
│   ├── main.tf            # EC2 + S3 + Security Group
│   ├── variables.tf       # Variables paramétrables
│   └── outputs.tf         # Outputs post-déploiement
├── tests/
│   └── test_agent.py      # 16 tests unitaires
├── docs/
│   └── JOURNAL.md         # Journal de bord 5 jours
├── logs/                  # Logs horodatés (ignorés par Git)
├── main.py                # CLI interactive
├── requirements.txt       # Dépendances Python
└── README.md              # Ce fichier

---

## Sécurité

- Les clés AWS ne sont **jamais** dans le code
- `.env` et `terraform.tfvars` sont dans `.gitignore`
- Le bucket S3 est privé par défaut
- `terraform.tfstate` est exclu de Git

---

## Auteur

**Doha Merini**
Projet réalisé en mai 2026
