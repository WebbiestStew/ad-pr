#!/bin/bash
# deploy_lambda.py
# Despliega la funcion Lambda de rollback usando LabRole
set -e

REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/LabRole"
FUNCTION_NAME="lab-rollback-function"
BUCKET_NAME="lab-bucket-mylab-339713126047"

echo "Empaquetando Lambda..."
zip lambda_rollback.zip lambda_rollback.py

echo "Subiendo a S3..."
aws s3 cp lambda_rollback.zip "s3://$BUCKET_NAME/lambda/lambda_rollback.zip"

echo "Creando funcion Lambda..."
aws lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --runtime python3.12 \
  --role "$ROLE_ARN" \
  --handler lambda_rollback.lambda_handler \
  --code "S3Bucket=$BUCKET_NAME,S3Key=lambda/lambda_rollback.zip" \
  --environment "Variables={S3_BUCKET=$BUCKET_NAME}" \
  --timeout 30 \
  --region "$REGION" 2>/dev/null && echo "Lambda creada" || \
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --s3-bucket "$BUCKET_NAME" \
  --s3-key "lambda/lambda_rollback.zip" \
  --region "$REGION" && echo "Lambda actualizada"

echo ""
echo "Probando Lambda con evento de fallo simulado..."
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --payload '{"detail":{"build-status":"FAILED","project-name":"lab-codebuild-project"}}' \
  --cli-binary-format raw-in-base64-out \
  --region "$REGION" \
  response.json

echo "Respuesta Lambda:"
cat response.json
echo ""
echo "Lambda desplegada exitosamente"
