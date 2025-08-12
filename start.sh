#!/bin/bash

echo "🚀 Iniciando QuickBooks Sales Reporter v2.0.0"
echo "📡 Configuración:"
echo "   • Flask Server: http://0.0.0.0:5000"
echo "   • OpenAPI Server: http://0.0.0.0:8080"
echo "   • Para OpenWebUI: http://localhost:8080"
echo "🏢 Desarrollado por KH LLOREDA, S.A."

# Verificar y crear directorios necesarios
mkdir -p /app/data /app/logs
chmod 755 /app/data /app/logs 2>/dev/null || true

# Verificar permisos de escritura
if [ ! -w /app/data ]; then
    echo "⚠️  Directorio /app/data no tiene permisos de escritura"
    echo "   Esto puede causar problemas con SQLite"
fi

# Verificar configuración
if [ -f .env.production ]; then
    echo "✅ Usando configuración de producción (.env.production)"
    export ENV_FILE=".env.production"
elif [ -f .env ]; then
    echo "✅ Usando configuración de desarrollo (.env)"
    export ENV_FILE=".env"
else
    echo "⚠️  No se encontró archivo de configuración (.env o .env.production)"
    echo "   Continuando con variables de entorno del sistema..."
    export ENV_FILE=""
fi

# Iniciar Flask en background
echo "🌐 Iniciando servidor Flask..."
export FLASK_ENV=production
python app.py &
FLASK_PID=$!

# Esperar que Flask se inicie
sleep 5

# Iniciar FastAPI (OpenWebUI)
echo "🚀 Iniciando servidor OpenAPI para OpenWebUI..."
cd /app
python openapi_server.py --host 0.0.0.0 --port 8080 &
FASTAPI_PID=$!

# Función para manejar señales de terminación
cleanup() {
    echo "🛑 Cerrando servidores..."
    kill $FLASK_PID $FASTAPI_PID 2>/dev/null
    wait $FLASK_PID $FASTAPI_PID 2>/dev/null
    echo "✅ Servidores cerrados correctamente"
    exit 0
}

# Capturar señales de terminación
trap cleanup SIGTERM SIGINT

# Esperar a que los procesos terminen
wait $FLASK_PID $FASTAPI_PID
