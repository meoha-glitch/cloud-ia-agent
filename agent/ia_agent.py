import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "mistral")


SYSTEM_PROMPT = """
You are an expert AWS cloud architect.
When a user describes a project or a need, you must respond ONLY with a
structured JSON object (no markdown, no explanation outside the JSON)
following this exact format:

{
  "architecture_name": "...",
  "description": "...",
  "components": [
    {
      "type": "EC2" | "S3" | "RDS" | "Lambda" | "VPC" | "SecurityGroup" | "other",
      "name": "...",
      "reason": "..."
    }
  ],
  "estimated_cost": "Free Tier eligible" | "Low" | "Medium" | "High",
  "terraform_ready": true | false
}
"""


def query_ollama(user_prompt: str) -> dict:
    """
    Envoie le prompt utilisateur à Ollama/Mistral
    et retourne la suggestion d'architecture sous forme de dict Python.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Ollama n'est pas accessible. Lance : ollama serve"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "Ollama met trop de temps à répondre (>120s). "
            "Vérifie les ressources de ta VM."
        )

    raw_text = response.json().get("response", "")

    try:
        architecture = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end   = raw_text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(
                f"Impossible de parser la réponse JSON de Mistral.\n"
                f"Réponse brute :\n{raw_text}"
            )
        architecture = json.loads(raw_text[start:end])

    return architecture


def display_architecture(architecture: dict) -> None:
    """
    Affiche la suggestion d'architecture de façon lisible dans le terminal.
    """
    print("\n" + "="*55)
    print(f"  Architecture : {architecture.get('architecture_name', 'N/A')}")
    print("="*55)
    print(f"\nDescription : {architecture.get('description', '')}\n")

    print("Composants AWS suggérés :")
    print("-"*40)
    for comp in architecture.get("components", []):
        print(f"  [{comp.get('type')}]  {comp.get('name')}")
        print(f"         → {comp.get('reason')}")
        print()

    print(f"Coût estimé     : {architecture.get('estimated_cost', 'N/A')}")
    print(f"Terraform ready : {architecture.get('terraform_ready', False)}")
    print("="*55 + "\n")
