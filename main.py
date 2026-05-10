import os
import sys
import json
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

from agent.ia_agent import query_ollama, display_architecture
from agent.aws_analyzer import get_aws_session, display_aws_inventory

load_dotenv()

TERRAFORM_DIR = os.path.join(os.path.dirname(__file__), "terraform")
LOG_FILE      = os.path.join(os.path.dirname(__file__), "logs", "deployment.log")


# ─── Logging ────────────────────────────────────────────────

def init_logging():
    """Crée le dossier logs s'il n'existe pas."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str, level: str = "INFO"):
    """Écrit un message dans le terminal ET dans le fichier de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ─── Terraform helpers ──────────────────────────────────────

def run_terraform(command: list, step_name: str) -> bool:
    """
    Exécute une commande Terraform et affiche la sortie en temps réel.
    Retourne True si succès, False sinon.
    """
    log(f"Terraform {step_name} — démarrage...")
    full_command = ["terraform"] + command

    process = subprocess.Popen(
        full_command,
        cwd=TERRAFORM_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        line = line.rstrip()
        if line:
            log(f"  {line}", level="TF")

    process.wait()

    if process.returncode == 0:
        log(f"Terraform {step_name} — SUCCÈS ✅", level="INFO")
        return True
    else:
        log(f"Terraform {step_name} — ÉCHEC ❌ (code {process.returncode})", level="ERROR")
        return False


def terraform_init() -> bool:
    return run_terraform(
        ["init", "-no-color"],
        "init"
    )


def terraform_validate() -> bool:
    return run_terraform(
        ["validate", "-no-color"],
        "validate"
    )


def terraform_plan() -> bool:
    return run_terraform(
        ["plan",
         "-var-file=terraform.tfvars",
         "-out=tfplan.out",
         "-no-color"],
        "plan"
    )


def terraform_apply() -> bool:
    return run_terraform(
        ["apply",
         "-auto-approve",
         "tfplan.out",
         "-no-color"],
        "apply"
    )


def terraform_destroy() -> bool:
    return run_terraform(
        ["destroy",
         "-var-file=terraform.tfvars",
         "-auto-approve",
         "-no-color"],
        "destroy"
    )


def get_terraform_outputs() -> dict:
    """Récupère les outputs Terraform après un apply."""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=TERRAFORM_DIR,
            capture_output=True,
            text=True
        )
        outputs = json.loads(result.stdout)
        return outputs
    except Exception as e:
        log(f"Impossible de lire les outputs Terraform : {e}", level="WARN")
        return {}


def display_outputs(outputs: dict):
    """Affiche les outputs du déploiement de façon lisible."""
    if not outputs:
        return

    print("\n" + "="*55)
    print("  RÉSULTAT DU DÉPLOIEMENT AWS")
    print("="*55)

    if "ec2_public_ip" in outputs:
        ip = outputs["ec2_public_ip"]["value"]
        print(f"\n  IP publique EC2  : {ip}")
        print(f"  URL HTTP         : http://{ip}")
        print(f"  Connexion SSH    : ssh -i cloud-ia-key ubuntu@{ip}")

    if "s3_bucket_name" in outputs:
        print(f"\n  Bucket S3        : {outputs['s3_bucket_name']['value']}")

    if "security_group_id" in outputs:
        print(f"  Security Group   : {outputs['security_group_id']['value']}")

    if "ec2_instance_id" in outputs:
        print(f"  Instance ID      : {outputs['ec2_instance_id']['value']}")

    print("="*55 + "\n")


# ─── Menus CLI ──────────────────────────────────────────────

def print_banner():
    print("\n" + "="*55)
    print("   CLOUD IA AGENT")
    print("   Déploiement AWS piloté par Intelligence Artificielle")
    print("   Stack : Python · Ollama · Terraform · boto3")
    print("="*55 + "\n")


def print_menu():
    print("Que veux-tu faire ?")
    print("")
    print("  [1] Analyser mon compte AWS (inventaire boto3)")
    print("  [2] Suggérer une architecture via IA (Ollama)")
    print("  [3] Déployer l'infrastructure (terraform apply)")
    print("  [4] Détruire l'infrastructure (terraform destroy)")
    print("  [5] Voir les outputs du dernier déploiement")
    print("  [6] Cycle complet (IA + init + validate + plan + apply)")
    print("  [0] Quitter")
    print("")


def action_inventaire():
    """Option 1 : inventaire AWS avec boto3."""
    log("Lancement de l'inventaire AWS...")
    session = get_aws_session()
    display_aws_inventory(session)


def action_suggestion_ia():
    """Option 2 : suggestion d'architecture via Ollama."""
    print("\nDécris ton projet cloud :")
    print("(ex: 'je veux héberger un site web avec stockage de fichiers')")
    print("")
    user_input = input("  Ton besoin : ").strip()

    if not user_input:
        log("Aucune entrée. Retour au menu.", level="WARN")
        return

    log("Envoi à Ollama/Mistral...")
    try:
        architecture = query_ollama(user_input)
        display_architecture(architecture)

        # Sauvegarde la suggestion dans un fichier JSON
        suggestion_path = os.path.join(
            os.path.dirname(__file__), "logs", "last_suggestion.json"
        )
        with open(suggestion_path, "w") as f:
            json.dump(architecture, f, indent=2)
        log(f"Suggestion sauvegardée dans {suggestion_path}")

    except ConnectionError as e:
        log(str(e), level="ERROR")
    except Exception as e:
        log(f"Erreur inattendue : {e}", level="ERROR")


def action_deploy():
    """Option 3 : terraform apply."""
    print("")
    print("⚠️  Tu vas déployer sur AWS (Free Tier).")
    confirm = input("   Confirmes-tu ? (oui/non) : ").strip().lower()
    if confirm != "oui":
        log("Déploiement annulé.")
        return

    log("=== DÉBUT DU DÉPLOIEMENT ===")
    start = time.time()

    success = terraform_apply()

    if success:
        elapsed = round(time.time() - start, 1)
        log(f"=== DÉPLOIEMENT TERMINÉ en {elapsed}s ===")
        outputs = get_terraform_outputs()
        display_outputs(outputs)
    else:
        log("Le déploiement a échoué. Vérifie les logs ci-dessus.", level="ERROR")


def action_destroy():
    """Option 4 : terraform destroy."""
    print("")
    print("⚠️  Tu vas SUPPRIMER toute l'infrastructure AWS.")
    print("    EC2 + S3 + Security Group seront détruits.")
    confirm = input("   Confirmes-tu ? (oui/non) : ").strip().lower()
    if confirm != "oui":
        log("Destruction annulée.")
        return

    log("=== DÉBUT DE LA DESTRUCTION ===")
    success = terraform_destroy()

    if success:
        log("=== INFRASTRUCTURE DÉTRUITE AVEC SUCCÈS ===")
    else:
        log("La destruction a échoué.", level="ERROR")


def action_outputs():
    """Option 5 : afficher les outputs."""
    outputs = get_terraform_outputs()
    if outputs:
        display_outputs(outputs)
    else:
        log("Aucun output disponible. Lance d'abord un déploiement.", level="WARN")


def action_cycle_complet():
    """Option 6 : cycle complet IA → init → validate → plan → apply."""
    print("")
    print("=== CYCLE COMPLET ===")
    print("Ce cycle va :")
    print("  1. Analyser ton besoin via Ollama/Mistral")
    print("  2. Initialiser Terraform")
    print("  3. Valider la configuration")
    print("  4. Planifier le déploiement")
    print("  5. Déployer sur AWS")
    print("")
    confirm = input("Confirmes-tu le cycle complet ? (oui/non) : ").strip().lower()
    if confirm != "oui":
        log("Cycle annulé.")
        return

    # Étape IA
    print("\nDécris ton projet cloud :")
    user_input = input("  Ton besoin : ").strip()
    if user_input:
        try:
            log("Analyse IA en cours...")
            architecture = query_ollama(user_input)
            display_architecture(architecture)
        except Exception as e:
            log(f"Erreur IA (non bloquante) : {e}", level="WARN")

    # Cycle Terraform
    log("=== DÉBUT DU CYCLE TERRAFORM ===")
    start = time.time()

    steps = [
        (terraform_init,     "init"),
        (terraform_validate, "validate"),
        (terraform_plan,     "plan"),
        (terraform_apply,    "apply"),
    ]

    for step_fn, step_name in steps:
        log(f"--- Étape : {step_name} ---")
        success = step_fn()
        if not success:
            log(f"Cycle interrompu à l'étape '{step_name}'.", level="ERROR")
            return
        time.sleep(1)

    elapsed = round(time.time() - start, 1)
    log(f"=== CYCLE COMPLET TERMINÉ en {elapsed}s ===")
    outputs = get_terraform_outputs()
    display_outputs(outputs)


# ─── Point d'entrée ─────────────────────────────────────────

def main():
    init_logging()
    print_banner()

    while True:
        print_menu()
        choice = input("  Ton choix : ").strip()

        if choice == "1":
            action_inventaire()
        elif choice == "2":
            action_suggestion_ia()
        elif choice == "3":
            action_deploy()
        elif choice == "4":
            action_destroy()
        elif choice == "5":
            action_outputs()
        elif choice == "6":
            action_cycle_complet()
        elif choice == "0":
            log("Au revoir !")
            sys.exit(0)
        else:
            print("  Choix invalide. Tape 0, 1, 2, 3, 4, 5 ou 6.")

        print("")
        input("  Appuie sur Entrée pour revenir au menu...")
        print("")


if __name__ == "__main__":
    main()
