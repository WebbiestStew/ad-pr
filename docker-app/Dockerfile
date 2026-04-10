# ─── STAGE 1: builder ─────────────────────────────────────────────────────────
# Instala dependencias en una imagen temporal
FROM python:3.12-slim AS builder

WORKDIR /app

# Copiar solo requirements primero (mejor cache)
COPY requirements.txt .

# Instalar dependencias en una carpeta local
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─── STAGE 2: runtime ─────────────────────────────────────────────────────────
# Imagen final limpia — sin pip, sin cache, mucho más pequeña
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /install /usr/local

# Copiar código de la app
COPY app.py .

# Variable de entorno
ENV APP_ENV=production

# Puerto que expone el contenedor
EXPOSE 5000

# Usar gunicorn como servidor de producción (no flask dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
