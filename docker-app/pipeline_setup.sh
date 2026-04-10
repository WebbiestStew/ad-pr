#!/bin/bash
# pipeline_setup.sh — configura CI/CD con S3 + CodeBuild
set -e

BUCKET_NAME="lab-bucket-mylab-339713126047"
PROJECT_NAME="lab-codebuild-project"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/LabRole"

echo "============================================"
echo " Configurando pipeline CI/CD"
echo " Bucket  : $BUCKET_NAME"
echo " Proyecto: $PROJECT_NAME"
echo "============================================"

# 1 — Crear bucket S3
echo ""
echo "[1/5] Creando bucket S3..."
if aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
    echo "  Bucket ya existe"
else
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
    echo "  Bucket creado: $BUCKET_NAME"
fi

# 2 — Subir codigo
echo ""
echo "[2/5] Subiendo codigo fuente a S3..."
zip -r source.zip app.py requirements.txt buildspec.yml test_app.py
aws s3 cp source.zip "s3://$BUCKET_NAME/source/source.zip"
echo "  Codigo subido"

# 3 — Crear proyecto CodeBuild
echo ""
echo "[3/5] Creando proyecto CodeBuild..."
aws codebuild create-project \
  --name "$PROJECT_NAME" \
  --source "{\"type\":\"S3\",\"location\":\"$BUCKET_NAME/source/source.zip\"}" \
  --artifacts "{\"type\":\"S3\",\"location\":\"$BUCKET_NAME\",\"path\":\"builds\",\"name\":\"app.zip\",\"packaging\":\"ZIP\"}" \
  --environment "{\"type\":\"LINUX_CONTAINER\",\"image\":\"aws/codebuild/standard:7.0\",\"computeType\":\"BUILD_GENERAL1_SMALL\",\"environmentVariables\":[{\"name\":\"S3_BUCKET\",\"value\":\"$BUCKET_NAME\",\"type\":\"PLAINTEXT\"}]}" \
  --service-role "$ROLE_ARN" \
  --region "$REGION" 2>/dev/null && echo "  Proyecto creado" || echo "  Proyecto ya existe"

# 4 — Iniciar build
echo ""
echo "[4/5] Iniciando build..."
BUILD_ID=$(aws codebuild start-build \
  --project-name "$PROJECT_NAME" \
  --region "$REGION" \
  --query "build.id" \
  --output text)
echo "  Build ID: $BUILD_ID"

# 5 — Esperar resultado
echo ""
echo "[5/5] Esperando resultado (2-3 minutos)..."
while true; do
    STATUS=$(aws codebuild batch-get-builds \
      --ids "$BUILD_ID" \
      --query "builds[0].buildStatus" \
      --output text)
    echo "  Estado: $STATUS"
    if [ "$STATUS" = "SUCCEEDED" ] || [ "$STATUS" = "FAILED" ] || [ "$STATUS" = "STOPPED" ]; then
        break
    fi
    sleep 15
done

echo ""
echo "============================================"
[ "$STATUS" = "SUCCEEDED" ] && echo " BUILD EXITOSO" || echo " BUILD FALLIDO"
echo "============================================"
