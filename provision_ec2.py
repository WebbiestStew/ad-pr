#!/usr/bin/env python3
"""
provision_ec2.py
Aprovisiona instancias EC2 respetando el límite de 9 del Learner Lab.
Uso: python3 provision_ec2.py
"""

import boto3
from botocore.exceptions import ClientError

# ─── CONFIG ───────────────────────────────────────────────────────────────────
REGION        = "us-east-1"
AMI_ID        = "ami-0c02fb55956c7d316"   # Amazon Linux 2 (us-east-1)
INSTANCE_TYPE = "t2.micro"
MAX_TOTAL     = 9                          # límite Learner Lab
# ──────────────────────────────────────────────────────────────────────────────

ec2 = boto3.client("ec2", region_name=REGION)


def get_running_count():
    """Cuenta instancias que NO están terminadas."""
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name",
                  "Values": ["pending", "running", "stopping", "stopped"]}]
    )
    count = 0
    for reservation in response["Reservations"]:
        count += len(reservation["Instances"])
    return count


def provision(num_instances: int, tag_name: str = "LearnerLab-Instance"):
    current = get_running_count()
    print(f"Instancias actuales (no terminadas): {current}")

    available = MAX_TOTAL - current
    if available <= 0:
        print(f"Límite alcanzado ({MAX_TOTAL}). No se pueden crear más instancias.")
        return

    to_launch = min(num_instances, available)
    if to_launch < num_instances:
        print(f"Solo se pueden crear {to_launch} instancia(s) (límite: {MAX_TOTAL}).")

    print(f"Lanzando {to_launch} instancia(s)...")

    try:
        response = ec2.run_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            MinCount=1,
            MaxCount=to_launch,
            TagSpecifications=[{
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": tag_name}]
            }]
        )

        for inst in response["Instances"]:
            print(f"  ✓ Creada: {inst['InstanceId']} — estado: {inst['State']['Name']}")

    except ClientError as e:
        print(f"Error al lanzar instancias: {e}")


if __name__ == "__main__":
    # Cambia este número según cuántas quieras crear
    provision(num_instances=2, tag_name="LearnerLab-Instance")
