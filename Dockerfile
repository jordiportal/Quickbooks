# Dockerfile actualizado para QuickBooks Sales Reporter con OpenWebUI
FROM python:3.11-slim

# Metadata
LABEL version="2.0.4-logging"
LABEL description="QuickBooks Sales Reporter con logging avanzado y error handling"
LABEL maintainer="KH LLOREDA, S.A."

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY quickbooks_client.py .
COPY quickbooks_logger.py .
COPY quickbooks_errors.py .
COPY app.py .
COPY openapi_server.py .
COPY sales_cache.py .
COPY scheduler.py .
COPY start.sh .

# Copiar templates HTML
COPY templates/ ./templates/

# Nota: Los archivos .env se montan como volúmenes en docker-compose.yml por seguridad

# Crear directorios para datos persistentes
RUN mkdir -p /app/data && mkdir -p /app/logs

# Hacer ejecutable el script de inicio
RUN chmod +x /app/start.sh

# Crear usuario no privilegiado y dar permisos
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/data && \
    chmod 755 /app/logs

USER appuser

# Exponer puertos
EXPOSE 5000 8080

# Comando de inicio
CMD ["/app/start.sh"]
