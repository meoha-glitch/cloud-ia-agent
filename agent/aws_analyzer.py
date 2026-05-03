import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-west-3")


def get_aws_session() -> boto3.Session:
    """
    Crée une session boto3 à partir des variables d'environnement.
    """
    return boto3.Session(
        aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name           = AWS_REGION
    )


def list_existing_ec2(session: boto3.Session) -> list:
    """
    Liste toutes les instances EC2 existantes sur le compte AWS.
    Retourne une liste de dicts avec id, type, état et nom.
    """
    ec2 = session.client("ec2")
    response = ec2.describe_instances()

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = "N/A"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]

            instances.append({
                "id":    instance["InstanceId"],
                "type":  instance["InstanceType"],
                "state": instance["State"]["Name"],
                "name":  name
            })

    return instances


def list_existing_s3(session: boto3.Session) -> list:
    """
    Liste tous les buckets S3 existants sur le compte AWS.
    """
    s3 = session.client("s3")
    response = s3.list_buckets()

    buckets = []
    for bucket in response.get("Buckets", []):
        buckets.append({
            "name":    bucket["Name"],
            "created": str(bucket["CreationDate"])
        })

    return buckets


def list_security_groups(session: boto3.Session) -> list:
    """
    Liste tous les Security Groups existants.
    """
    ec2 = session.client("ec2")
    response = ec2.describe_security_groups()

    groups = []
    for sg in response["SecurityGroups"]:
        groups.append({
            "id":          sg["GroupId"],
            "name":        sg["GroupName"],
            "description": sg["Description"]
        })

    return groups


def display_aws_inventory(session: boto3.Session) -> None:
    """
    Affiche un inventaire complet des ressources AWS existantes.
    """
    print("\n" + "="*55)
    print("  INVENTAIRE AWS ACTUEL")
    print("="*55)

    # EC2
    print("\nInstances EC2 :")
    print("-"*40)
    instances = list_existing_ec2(session)
    if instances:
        for inst in instances:
            print(f"  {inst['id']} | {inst['type']} | "
                  f"{inst['state']} | {inst['name']}")
    else:
        print("  Aucune instance EC2 trouvée.")

    # S3
    print("\nBuckets S3 :")
    print("-"*40)
    buckets = list_existing_s3(session)
    if buckets:
        for b in buckets:
            print(f"  {b['name']} | créé le {b['created']}")
    else:
        print("  Aucun bucket S3 trouvé.")

    # Security Groups
    print("\nSecurity Groups :")
    print("-"*40)
    sgs = list_security_groups(session)
    for sg in sgs:
        print(f"  {sg['id']} | {sg['name']} | {sg['description']}")

    print("="*55 + "\n")
