import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

from unittest.mock import patch, MagicMock
from agent.ia_agent import query_ollama, display_architecture
from agent.aws_analyzer import (
    get_aws_session,
    list_existing_ec2,
    list_existing_s3,
    list_security_groups
)


# ─── Données de test ────────────────────────────────────────

FAKE_ARCHITECTURE = {
    "architecture_name": "Simple Web App",
    "description": "A basic web application architecture.",
    "components": [
        {
            "type": "EC2",
            "name": "web-server",
            "reason": "Hosts the application"
        },
        {
            "type": "S3",
            "name": "static-bucket",
            "reason": "Stores static files"
        },
        {
            "type": "SecurityGroup",
            "name": "web-sg",
            "reason": "Controls traffic"
        }
    ],
    "estimated_cost": "Free Tier eligible",
    "terraform_ready": True
}


# ─── Tests ia_agent.py ──────────────────────────────────────

class TestQueryOllama:

    @patch("agent.ia_agent.requests.post")
    def test_retourne_dict_valide(self, mock_post):
        """Ollama répond un JSON valide → on obtient un dict."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": json.dumps(FAKE_ARCHITECTURE)
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = query_ollama("I need a simple web app")
        assert isinstance(result, dict)
        assert result["architecture_name"] == "Simple Web App"
        assert len(result["components"]) == 3

    @patch("agent.ia_agent.requests.post")
    def test_json_embarque_dans_texte(self, mock_post):
        """Mistral ajoute du texte autour du JSON → extraction robuste."""
        raw = f"Here is the architecture:\n{json.dumps(FAKE_ARCHITECTURE)}\nHope this helps!"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": raw}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = query_ollama("web app")
        assert result["terraform_ready"] is True

    @patch("agent.ia_agent.requests.post")
    def test_connection_error(self, mock_post):
        """Ollama injoignable → ConnectionError avec message clair."""
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError()

        with pytest.raises(ConnectionError) as exc:
            query_ollama("web app")
        assert "ollama serve" in str(exc.value).lower()

    def test_display_architecture_sans_crash(self, capsys):
        """display_architecture ne plante pas et affiche les composants."""
        display_architecture(FAKE_ARCHITECTURE)
        captured = capsys.readouterr()
        assert "Simple Web App" in captured.out
        assert "EC2" in captured.out
        assert "Free Tier eligible" in captured.out


# ─── Tests aws_analyzer.py ──────────────────────────────────

class TestAwsAnalyzer:

    @patch("agent.aws_analyzer.boto3.Session")
    def test_list_ec2_vide(self, mock_session_class):
        """Aucune instance EC2 → liste vide retournée."""
        mock_session = MagicMock()
        mock_ec2 = MagicMock()
        mock_ec2.describe_instances.return_value = {"Reservations": []}
        mock_session.client.return_value = mock_ec2
        mock_session_class.return_value = mock_session

        session = get_aws_session()
        result = list_existing_ec2(session)
        assert result == []

    @patch("agent.aws_analyzer.boto3.Session")
    def test_list_ec2_avec_instance(self, mock_session_class):
        """Une instance EC2 existante → retournée correctement."""
        mock_session = MagicMock()
        mock_ec2 = MagicMock()
        mock_ec2.describe_instances.return_value = {
            "Reservations": [{
                "Instances": [{
                    "InstanceId":   "i-0abc123",
                    "InstanceType": "t2.micro",
                    "State":        {"Name": "running"},
                    "Tags":         [{"Key": "Name", "Value": "web-server"}]
                }]
            }]
        }
        mock_session.client.return_value = mock_ec2
        mock_session_class.return_value = mock_session

        session = get_aws_session()
        result = list_existing_ec2(session)
        assert len(result) == 1
        assert result[0]["id"]    == "i-0abc123"
        assert result[0]["state"] == "running"
        assert result[0]["name"]  == "web-server"

    @patch("agent.aws_analyzer.boto3.Session")
    def test_list_s3_vide(self, mock_session_class):
        """Aucun bucket S3 → liste vide retournée."""
        mock_session = MagicMock()
        mock_s3 = MagicMock()
        mock_s3.list_buckets.return_value = {"Buckets": []}
        mock_session.client.return_value = mock_s3
        mock_session_class.return_value = mock_session

        session = get_aws_session()
        result = list_existing_s3(session)
        assert result == []

    @patch("agent.aws_analyzer.boto3.Session")
    def test_list_security_groups(self, mock_session_class):
        """Un Security Group existant → retourné correctement."""
        mock_session = MagicMock()
        mock_ec2 = MagicMock()
        mock_ec2.describe_security_groups.return_value = {
            "SecurityGroups": [{
                "GroupId":     "sg-0abc123",
                "GroupName":   "web-sg",
                "Description": "Web security group"
            }]
        }
        mock_session.client.return_value = mock_ec2
        mock_session_class.return_value = mock_session

        session = get_aws_session()
        result = list_security_groups(session)
        assert len(result) == 1
        assert result[0]["name"] == "web-sg"
