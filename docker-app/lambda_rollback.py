"""
lambda_rollback.py
Funcion Lambda que detecta fallos en CodeBuild y hace rollback
restaurando la version anterior del artefacto en S3.
"""

import boto3
import os
import json
from datetime import datetime

s3 = boto3.client("s3")
sns = boto3.client("sns")

S3_BUCKET = os.environ.get("S3_BUCKET", "")
BACKUP_KEY = "builds/backup/app.zip"
CURRENT_KEY = "builds/app.zip"
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def lambda_handler(event, context):
    print(f"Evento recibido: {json.dumps(event)}")

    detail = event.get("detail", {})
    build_status = detail.get("build-status", "")
    project_name = detail.get("project-name", "unknown")

    print(f"Proyecto: {project_name} -- Estado: {build_status}")

    if build_status != "FAILED":
        print("Build exitoso, no se necesita rollback.")
        return {"statusCode": 200, "body": "No rollback needed"}

    print("Build FALLIDO -- iniciando rollback...")

    try:
        s3.head_object(Bucket=S3_BUCKET, Key=BACKUP_KEY)

        s3.copy_object(
            Bucket=S3_BUCKET,
            CopySource={"Bucket": S3_BUCKET, "Key": BACKUP_KEY},
            Key=CURRENT_KEY
        )

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        message = f"ROLLBACK ejecutado\nProyecto: {project_name}\nHora: {timestamp}"
        print(message)

        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="[ROLLBACK] Pipeline restaurado",
                Message=message
            )

        return {"statusCode": 200, "body": "Rollback completado"}

    except Exception as e:
        print(f"Error durante rollback: {str(e)}")
        return {"statusCode": 500, "body": f"Rollback failed: {str(e)}"}
