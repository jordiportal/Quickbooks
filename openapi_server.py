#!/usr/bin/env python3
"""
🚀 QuickBooks Sales Reporter - OpenAPI Server Minimal
Servidor simplificado para OpenWebUI con solo los endpoints esenciales
"""

import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uvicorn
import argparse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openapi_server")

# Configuración
FLASK_BASE_URL = "http://localhost:5000"

# Crear aplicación FastAPI
app = FastAPI(
    title="QuickBooks Sales Reporter",
    description="🧠 Servidor simplificado para consultas SQL inteligentes con OpenWebUI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class SQLQuery(BaseModel):
    sql: str

class UpdateResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

# Cliente HTTP
http_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("startup")
async def startup_event():
    """Verificar conexión con Flask al iniciar"""
    logger.info("🚀 Iniciando QuickBooks Sales Reporter API Server...")
    logger.info(f"📡 Conectando con servidor Flask en: {FLASK_BASE_URL}")
    
    try:
        response = await http_client.get(f"{FLASK_BASE_URL}/health")
        if response.status_code == 200:
            logger.info("✅ Conexión con servidor Flask establecida")
        else:
            logger.warning(f"⚠️ Flask responde con código: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ No se puede conectar con el servidor Flask: {e}")
        logger.error("   Asegúrate de que la aplicación principal esté ejecutándose en http://localhost:5000")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    logger.info("🛑 Cerrando QuickBooks Sales Reporter API Server...")
    await http_client.aclose()

@app.get("/", include_in_schema=False)
async def root():
    """Endpoint raíz - redirigir a documentación"""
    return {
        "message": "🧠 QuickBooks Sales Reporter para OpenWebUI",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET /api/schema - Esquema de base de datos",
            "POST /api/query/sql - Ejecutar consulta SQL",
            "GET /api/status - Estado y tamaño de BBDD",
            "POST /admin/force-update - Forzar actualización"
        ]
    }

@app.get("/api/schema")
async def get_database_schema():
    """
    📋 Obtener esquema completo de la base de datos
    
    Devuelve la estructura de todas las tablas, columnas, tipos de datos,
    y ejemplos de consultas SQL para que OpenWebUI pueda generar consultas inteligentes.
    """
    try:
        response = await http_client.get(f"{FLASK_BASE_URL}/api/schema")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Error obteniendo esquema: {response.status_code}"
            )
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, 
            detail="No se puede conectar con el servidor Flask. Asegúrate de que esté ejecutándose en puerto 5000."
        )
    except Exception as e:
        logger.error(f"Error obteniendo esquema: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/api/query/sql")
async def execute_sql_query(query: SQLQuery):
    """
    🧠 Ejecutar consulta SQL en la base de datos
    
    Permite ejecutar consultas SELECT en las tablas sales_cache, product_sales y customer_sales.
    Solo se permiten consultas de lectura por seguridad.
    
    Ejemplos de consultas útiles:
    - SELECT period, total_sales, total_units FROM sales_cache WHERE period LIKE '%/2025' ORDER BY period
    - SELECT product_name, SUM(units_sold) as total_units FROM product_sales GROUP BY product_name ORDER BY total_units DESC LIMIT 5
    - SELECT customer_name, SUM(total_sales) as total_spent FROM customer_sales GROUP BY customer_name ORDER BY total_spent DESC LIMIT 5
    """
    try:
        # Validación básica de seguridad
        sql_upper = query.sql.upper().strip()
        
        # Solo permitir SELECT
        if not sql_upper.startswith('SELECT'):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten consultas SELECT por seguridad"
            )
        
        # Prohibir palabras peligrosas
        forbidden_words = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for word in forbidden_words:
            if word in sql_upper:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Palabra prohibida: {word}. Solo se permiten consultas de lectura."
                )
        
        # Enviar consulta al servidor Flask
        response = await http_client.post(
            f"{FLASK_BASE_URL}/api/query/sql",
            json={"sql": query.sql},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = "Error ejecutando consulta SQL"
            try:
                error_json = response.json()
                error_detail = error_json.get('error', error_detail)
            except:
                pass
            
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se puede conectar con el servidor Flask"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ejecutando consulta SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/api/status")
async def get_database_status():
    """
    📊 Obtener estado y tamaño de la base de datos
    
    Devuelve información sobre:
    - Número total de registros en cada tabla
    - Última actualización
    - Estado del cache
    - Estadísticas de uso
    """
    try:
        response = await http_client.get(f"{FLASK_BASE_URL}/api/public/status")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error obteniendo estado: {response.status_code}"
            )
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se puede conectar con el servidor Flask"
        )
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/admin/force-update")
async def force_update():
    """
    🔄 Forzar actualización de datos desde QuickBooks
    
    Inicia una actualización manual de todos los datos desde QuickBooks Online.
    Útil cuando necesitas datos frescos inmediatamente sin esperar la actualización automática.
    
    ⚠️ Nota: Requiere que la aplicación principal tenga tokens válidos de QuickBooks.
    """
    try:
        response = await http_client.post(f"{FLASK_BASE_URL}/admin/force-update")
        
        if response.status_code == 200:
            result = response.json()
            return UpdateResponse(
                success=True,
                message="Actualización iniciada correctamente",
                details=result
            )
        else:
            error_detail = "Error forzando actualización"
            try:
                error_json = response.json()
                error_detail = error_json.get('error', error_detail)
            except:
                pass
            
            return UpdateResponse(
                success=False,
                message=error_detail,
                details={"status_code": response.status_code}
            )
            
    except httpx.ConnectError:
        return UpdateResponse(
            success=False,
            message="No se puede conectar con el servidor Flask. Asegúrate de que esté ejecutándose.",
            details={"error": "Connection refused"}
        )
    except Exception as e:
        logger.error(f"Error forzando actualización: {e}")
        return UpdateResponse(
            success=False,
            message=f"Error interno: {str(e)}",
            details={"exception": str(e)}
        )

# Manejo de errores global
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "available_endpoints": [
                "GET /api/schema",
                "POST /api/query/sql", 
                "GET /api/status",
                "POST /admin/force-update"
            ],
            "docs": "/docs"
        }
    )

def main():
    """Función principal para iniciar el servidor"""
    parser = argparse.ArgumentParser(description="QuickBooks Sales Reporter OpenAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host para el servidor")
    parser.add_argument("--port", type=int, default=8080, help="Puerto para el servidor")
    parser.add_argument("--flask-url", default="http://localhost:5000", help="URL del servidor Flask")
    
    args = parser.parse_args()
    
    # Actualizar configuración global
    global FLASK_BASE_URL
    FLASK_BASE_URL = args.flask_url
    
    print("🚀 Iniciando QuickBooks Sales Reporter OpenAPI Server")
    print("📡 Configuración:")
    print(f"   • API Server: http://{args.host}:{args.port}")
    print(f"   • Flask Server: {args.flask_url}")
    print(f"   • Documentación: http://{args.host}:{args.port}/docs")
    print(f"   • OpenAPI Spec: http://{args.host}:{args.port}/openapi.json")
    print("🔗 Para OpenWebUI:")
    print("   1. Agrega este servidor como herramienta OpenAPI")
    print(f"   2. URL: http://{args.host}:{args.port}")
    print("   3. Haz preguntas como: '¿Cuáles son los productos más vendidos?'")
    print("📋 Endpoints disponibles:")
    print("   • GET /api/schema - Esquema de base de datos")
    print("   • POST /api/query/sql - Ejecutar consulta SQL")
    print("   • GET /api/status - Estado y tamaño de BBDD")
    print("   • POST /admin/force-update - Forzar actualización")
    print("🏢 Desarrollado por KH LLOREDA, S.A.")
    
    uvicorn.run(
        "openapi_server:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
