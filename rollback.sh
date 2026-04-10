#!/bin/bash
echo "Build failed — ejecutando rollback..."
docker stop $(docker ps -q) 2>/dev/null || true
docker run -d -p 8080:80 nginx:latest
echo "Rollback completado — nginx default corriendo"
