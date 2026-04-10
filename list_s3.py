#!/usr/bin/env python3
"""
list_s3.py
Lista todos los buckets S3 y sus objetos usando Boto3.
Uso: python3 list_s3.py
"""

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

s3 = boto3.client("s3", region_name=REGION)


def list_buckets_and_objects():
    print("\n📋 Listando buckets S3...\n")

    try:
        response = s3.list_buckets()
        buckets  = response.get("Buckets", [])

        if not buckets:
            print("No se encontraron buckets en esta cuenta.")
            return

        print(f"Total de buckets: {len(buckets)}\n")
        print("-" * 60)

        for bucket in buckets:
            bname   = bucket["Name"]
            created = bucket["CreationDate"].strftime("%Y-%m-%d %H:%M UTC")

            print(f"\n🪣  Bucket : {bname}")
            print(f"   Creado : {created}")

            try:
                paginator = s3.get_paginator("list_objects_v2")
                pages     = paginator.paginate(Bucket=bname)

                obj_count  = 0
                total_size = 0

                for page in pages:
                    for obj in page.get("Contents", []):
                        obj_count  += 1
                        total_size += obj["Size"]
                        size_kb     = obj["Size"] / 1024
                        modified    = obj["LastModified"].strftime("%Y-%m-%d")
                        print(f"   📄 {obj['Key']:<40} {size_kb:>8.1f} KB   {modified}")

                if obj_count == 0:
                    print("   (bucket vacío)")
                else:
                    print(f"\n   Subtotal: {obj_count} objeto(s) — {total_size/1024:.1f} KB total")

            except ClientError as e:
                code = e.response["Error"]["Code"]
                print(f"   ⚠ No se pudo acceder: {code}")

        print("\n" + "-" * 60)
        print("Listado completo.\n")

    except ClientError as e:
        print(f"Error al conectar con S3: {e}")


if __name__ == "__main__":
    list_buckets_and_objects()
