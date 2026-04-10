#!/usr/bin/env python3
"""
resource_report.py
Genera un reporte automático de uso de recursos en AWS (EC2 + S3).
Uso: python3 resource_report.py
"""

import boto3
from datetime import datetime
from botocore.exceptions import ClientError

REGION = "us-east-1"

ec2 = boto3.client("ec2", region_name=REGION)
s3  = boto3.client("s3",  region_name=REGION)


def report_ec2():
    print("\n" + "="*50)
    print("  EC2 — Instancias")
    print("="*50)

    response = ec2.describe_instances()
    total = 0

    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            total += 1
            name = next(
                (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                "(sin nombre)"
            )
            state  = inst["State"]["Name"]
            itype  = inst["InstanceType"]
            iid    = inst["InstanceId"]
            az     = inst["Placement"]["AvailabilityZone"]
            launch = inst["LaunchTime"].strftime("%Y-%m-%d %H:%M UTC")

            status_icon = {"running": "🟢", "stopped": "🔴", "terminated": "⚫"}.get(state, "🟡")

            print(f"\n  {status_icon} {name}")
            print(f"     ID     : {iid}")
            print(f"     Tipo   : {itype}")
            print(f"     Estado : {state}")
            print(f"     AZ     : {az}")
            print(f"     Lanzada: {launch}")

    print(f"\n  Total instancias: {total}")


def report_s3():
    print("\n" + "="*50)
    print("  S3 — Buckets y objetos")
    print("="*50)

    try:
        buckets = s3.list_buckets().get("Buckets", [])
        if not buckets:
            print("\n  No hay buckets en esta cuenta.")
            return

        for bucket in buckets:
            bname = bucket["Name"]
            created = bucket["CreationDate"].strftime("%Y-%m-%d")
            print(f"\n  📦 {bname}  (creado: {created})")

            try:
                objects = s3.list_objects_v2(Bucket=bname)
                contents = objects.get("Contents", [])
                if not contents:
                    print("     (bucket vacío)")
                else:
                    total_size = 0
                    for obj in contents[:10]:  # muestra máximo 10
                        size_kb = obj["Size"] / 1024
                        print(f"     • {obj['Key']}  ({size_kb:.1f} KB)")
                        total_size += obj["Size"]
                    if len(contents) > 10:
                        print(f"     ... y {len(contents)-10} objeto(s) más")
                    print(f"     Total: {len(contents)} objetos — {total_size/1024:.1f} KB")
            except ClientError as e:
                print(f"     No se pudo listar: {e.response['Error']['Code']}")

    except ClientError as e:
        print(f"  Error al listar buckets: {e}")


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"  REPORTE DE RECURSOS AWS")
    print(f"  Generado: {now}")
    print(f"  Región  : {REGION}")
    print(f"{'='*50}")

    report_ec2()
    report_s3()

    print("\n" + "="*50)
    print("  Fin del reporte")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
