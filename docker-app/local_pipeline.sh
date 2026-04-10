#!/bin/bash
# local_pipeline.sh
# Simula pipeline CI/CD: install → test → build → deploy → rollback
set -e

BUCKET="lab-bucket-mylab-339713126047"

echo "========================================"
echo " PIPELINE CI/CD — Simulacion local"
echo "========================================"

echo ""
echo "[1/4] INSTALL — instalando dependencias..."
pip3 install -r requirements.txt --break-system-packages -q
echo "  Dependencias instaladas"

echo ""
echo "[2/4] TEST — ejecutando pruebas..."
pip3 install pytest --break-system-packages -q
python3 -m pytest test_app.py -v
echo "  Pruebas pasadas"

echo ""
echo "[3/4] BUILD — empaquetando aplicacion..."
zip -r app.zip app.py requirements.txt buildspec.yml
echo "  Paquete creado: app.zip"

echo ""
echo "[4/4] DEPLOY — subiendo artefacto a S3..."
# Backup version anterior si existe
aws s3 cp "s3://$BUCKET/builds/app.zip" \
  "s3://$BUCKET/builds/backup/app.zip" 2>/dev/null && \
  echo "  Backup creado" || echo "  No habia version anterior"

# Subir nueva version
aws s3 cp app.zip "s3://$BUCKET/builds/app.zip"
echo "  Artefacto desplegado en s3://$BUCKET/builds/app.zip"

echo ""
echo "========================================"
echo " PIPELINE COMPLETADO EXITOSAMENTE"
echo "========================================"
