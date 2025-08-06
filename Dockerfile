# Dockerfile simple para QuickBooks Online App
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código de la aplicación
COPY quickbooks_client.py .
COPY app.py .
COPY sales_cache.py .
COPY scheduler.py .
COPY templates/ ./templates/

# Crear directorios para datos persistentes
RUN mkdir -p /app/data && mkdir -p /app/logs

# Crear usuario no privilegiado
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando de inicio con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]