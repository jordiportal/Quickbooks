#!/bin/bash
# Script simple de despliegue para QuickBooks Online App

echo "🚀 Desplegando aplicación QuickBooks (solo contenedor)..."

# Verificar que Docker esté disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar archivo de configuración
if [ ! -f ".env.production" ]; then
    echo "📝 Creando archivo .env.production desde ejemplo..."
    cp config.production.env .env.production
    echo "⚠️  Edita .env.production con tus credenciales antes de continuar"
    exit 1
fi

# Construir imagen
echo "🔨 Construyendo imagen..."
docker build -f Dockerfile.simple -t quickbooks-app .

# Detener contenedor existente si existe
echo "⏹️  Deteniendo contenedor anterior..."
docker stop quickbooks-app 2>/dev/null || true
docker rm quickbooks-app 2>/dev/null || true

# Iniciar nuevo contenedor
echo "🚀 Iniciando contenedor..."
docker run -d \
    --name quickbooks-app \
    --restart unless-stopped \
    -p 8000:8000 \
    --env-file .env.production \
    -v "$(pwd)/logs:/app/logs" \
    quickbooks-app

# Verificar que esté funcionando
echo "✅ Verificando estado..."
sleep 5

if docker ps | grep -q quickbooks-app; then
    echo "🎉 ¡Aplicación desplegada exitosamente!"
    echo "📍 Disponible en: http://localhost:8000"
    echo "🔗 Configura tu Nginx para hacer proxy a este puerto"
else
    echo "❌ Error al iniciar el contenedor"
    docker logs quickbooks-app
    exit 1
fi