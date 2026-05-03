import sys
from agent.ia_agent import query_ollama, display_architecture
from agent.aws_analyzer import get_aws_session, display_aws_inventory


def main():
    print("\n" + "="*55)
    print("   CLOUD IA AGENT — Déploiement AWS piloté par IA")
    print("="*55)

    # Étape 1 : inventaire AWS actuel
    print("\n[1/3] Connexion à AWS et inventaire des ressources...")
    session = get_aws_session()
    display_aws_inventory(session)

    # Étape 2 : requête utilisateur
    print("[2/3] Décris ton projet cloud (ex: 'je veux héberger")
    print("       un site web avec stockage de fichiers') :")
    print()
    user_input = input("  Ton besoin : ").strip()

    if not user_input:
        print("Aucune entrée détectée. Arrêt.")
        sys.exit(1)

    # Étape 3 : suggestion IA
    print("\n[3/3] Analyse en cours par Mistral... (peut prendre")
    print("       10 à 30 secondes)\n")
    architecture = query_ollama(user_input)
    display_architecture(architecture)

    print("Suggestion générée avec succès !")
    print("Jour 3 : ces composants seront provisionnés via Terraform.\n")


if __name__ == "__main__":
    main()
