#!/usr/bin/env python3
"""
QuickBooks Sales Reporter - OpenAPI Server for OpenWebUI Integration

Este servidor expone los datos de ventas de QuickBooks Online a través de una API REST estándar
compatible con OpenWebUI, permitiendo consultas de chat sobre ventas empresariales.

Uso:
    python openapi_server.py
    # O con parámetros específicos:
    python openapi_server.py --host 0.0.0.0 --port 8080

Ejemplos de consultas en OpenWebUI:
    - "¿Cómo van las ventas de este mes?"
    - "¿Cuál fue el mejor mes del año?"
    - "Muéstrame las ventas anuales de 2024"
    - "¿Cuántas facturas se emitieron en julio?"

Desarrollado por KH LLOREDA, S.A.
"""

import argparse
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import requests
from typing import Optional, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del servidor Flask principal
FLASK_BASE_URL = "http://localhost:5000"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando QuickBooks Sales Reporter API Server...")
    logger.info(f"📡 Conectando con servidor Flask en: {FLASK_BASE_URL}")
    
    # Verificar conexión con el servidor Flask
    try:
        response = requests.get(f"{FLASK_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Conexión con servidor Flask establecida")
        else:
            logger.warning(f"⚠️ Servidor Flask responde con código: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ No se puede conectar con el servidor Flask: {e}")
        logger.error("   Asegúrate de que la aplicación principal esté ejecutándose en http://localhost:5000")
    
    yield
    
    logger.info("🛑 Cerrando QuickBooks Sales Reporter API Server...")

# Crear aplicación FastAPI
app = FastAPI(
    title="QuickBooks Sales Reporter API",
    description="""
API REST para consultar datos de ventas de QuickBooks Online con cache automático.

Este servidor actúa como un proxy API estándar para el sistema QuickBooks Sales Reporter,
proporcionando endpoints compatibles con OpenWebUI para consultas de chat sobre ventas.

**Características principales:**
- 📊 Consultas de ventas mensuales y anuales
- 📈 Análisis de tendencias y reportes automáticos  
- 🔄 Cache inteligente con actualizaciones programadas
- 🎯 Compatible con OpenWebUI para consultas en lenguaje natural
- 🛠️ Funciones administrativas para gestión del sistema

**Desarrollado por:** KH LLOREDA, S.A.
    """,
    version="2.0.0",
    contact={
        "name": "KH LLOREDA, S.A.",
        "email": "lopd@khlloreda.com",
        "url": "https://github.com/jordiportal/Quickbooks"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {"name": "sales", "description": "Consultas de datos de ventas"},
        {"name": "annual", "description": "Reportes y análisis anuales"},
        {"name": "admin", "description": "Funciones administrativas y cache"},
        {"name": "system", "description": "Estado del sistema y estadísticas"}
    ],
    lifespan=lifespan
)

# Configurar CORS para OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios concretos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función helper para hacer peticiones al servidor Flask
async def flask_request(endpoint: str, method: str = "GET", **kwargs) -> Dict[Any, Any]:
    """
    Realiza peticiones al servidor Flask principal
    
    Args:
        endpoint: Endpoint del servidor Flask (ej. '/api/sales')
        method: Método HTTP ('GET', 'POST', etc.)
        **kwargs: Argumentos adicionales para requests
        
    Returns:
        Respuesta JSON del servidor Flask
        
    Raises:
        HTTPException: Si hay error en la comunicación o autenticación
    """
    url = f"{FLASK_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=30, **kwargs)
        else:
            response = requests.request(method, url, timeout=30, **kwargs)
        
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="No autenticado con QuickBooks. Por favor, autoriza primero en http://localhost:5000"
            )
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para los parámetros especificados"
            )
        elif response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error del servidor: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Timeout conectando con QuickBooks. El servidor puede estar procesando datos."
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="No se puede conectar con el servidor QuickBooks. Verifica que esté ejecutándose en http://localhost:5000"
        )
    except Exception as e:
        logger.error(f"Error en petición Flask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE VENTAS
# ============================================================================

@app.get("/api/sales", tags=["sales"])
async def get_current_month_sales():
    """
    📊 Obtener ventas del mes actual
    
    Retorna los datos de ventas del mes actual con detalles de facturas y recibos.
    Los datos se obtienen del cache cuando están disponibles.
    
    **Ejemplo de uso en OpenWebUI:**
    "¿Cómo van las ventas de este mes?"
    """
    return await flask_request("/api/sales")

@app.get("/api/sales/{year}/{month}", tags=["sales"])
async def get_specific_month_sales(year: int, month: int):
    """
    📅 Obtener ventas de un mes específico
    
    Retorna los datos de ventas para un año y mes específicos.
    Útil para consultar datos históricos o comparar períodos.
    
    **Ejemplo de uso en OpenWebUI:**
    "¿Cuánto vendimos en julio de 2024?"
    """
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="Año debe estar entre 2020 y 2030")
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
    
    return await flask_request(f"/sales/{year}/{month}")

# ============================================================================
# ENDPOINTS ANUALES
# ============================================================================

@app.get("/api/annual", tags=["annual"])
async def get_current_year_report():
    """
    📈 Obtener reporte anual del año actual
    
    Retorna un reporte completo de ventas anuales con desglose mensual,
    análisis de tendencias, mejor/peor mes, y estadísticas agregadas.
    
    **Ejemplo de uso en OpenWebUI:**
    "Muéstrame el resumen anual de ventas"
    """
    return await flask_request("/annual")

@app.get("/api/annual/{year}", tags=["annual"])
async def get_specific_year_report(year: int):
    """
    📊 Obtener reporte anual de un año específico
    
    Retorna un reporte completo de ventas para un año específico.
    Incluye análisis comparativo y datos históricos.
    
    **Ejemplo de uso en OpenWebUI:**
    "¿Cómo fueron las ventas en 2023?"
    """
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="Año debe estar entre 2020 y 2030")
    
    return await flask_request(f"/annual/{year}")

@app.get("/api/quarterly/{year}", tags=["annual"])
async def get_quarterly_report(year: int):
    """
    📊 Obtener reporte trimestral
    
    Retorna datos de ventas agrupados por trimestres para un año específico.
    Útil para análisis de tendencias estacionales.
    
    **Ejemplo de uso en OpenWebUI:**
    "¿Cuál fue el mejor trimestre de 2024?"
    """
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="Año debe estar entre 2020 y 2030")
    
    # Este endpoint necesita ser implementado en el servidor Flask
    # Por ahora retornamos el reporte anual y lo procesamos
    annual_data = await flask_request(f"/annual/{year}")
    
    # Convertir datos anuales a formato trimestral
    quarterly_data = {
        "año": year,
        "total_anual": annual_data.get("total_anual", 0),
        "trimestres": {
            "Q1": {"nombre": "Primer Trimestre (Ene-Mar)", "total": 0, "meses": {}},
            "Q2": {"nombre": "Segundo Trimestre (Abr-Jun)", "total": 0, "meses": {}},
            "Q3": {"nombre": "Tercer Trimestre (Jul-Sep)", "total": 0, "meses": {}},
            "Q4": {"nombre": "Cuarto Trimestre (Oct-Dic)", "total": 0, "meses": {}}
        }
    }
    
    quarters = {
        "Q1": ["01", "02", "03"],
        "Q2": ["04", "05", "06"], 
        "Q3": ["07", "08", "09"],
        "Q4": ["10", "11", "12"]
    }
    
    for quarter, months in quarters.items():
        for month_key in months:
            if month_key in annual_data.get("meses", {}):
                month_data = annual_data["meses"][month_key]
                quarterly_data["trimestres"][quarter]["meses"][month_key] = month_data
                quarterly_data["trimestres"][quarter]["total"] += month_data["data"]["total_ventas"]
    
    return quarterly_data

@app.get("/api/comparison/{year1}/{year2}", tags=["annual"])
async def compare_years(year1: int, year2: int):
    """
    🔄 Comparar ventas entre dos años
    
    Compara los datos de ventas entre dos años y calcula diferencias,
    porcentajes de crecimiento/decrecimiento y tendencias.
    
    **Ejemplo de uso en OpenWebUI:**
    "Compara las ventas de 2024 con 2023"
    """
    if year1 < 2020 or year1 > 2030 or year2 < 2020 or year2 > 2030:
        raise HTTPException(status_code=400, detail="Los años deben estar entre 2020 y 2030")
    
    # Obtener datos de ambos años
    try:
        data_year1 = await flask_request(f"/annual/{year1}")
        data_year2 = await flask_request(f"/annual/{year2}")
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para uno de los años especificados")
        raise
    
    # Calcular comparación
    ventas_year1 = data_year1.get("total_anual", 0)
    ventas_year2 = data_year2.get("total_anual", 0)
    diferencia = ventas_year1 - ventas_year2
    
    if ventas_year2 > 0:
        porcentaje_cambio = (diferencia / ventas_year2) * 100
    else:
        porcentaje_cambio = 0
    
    if diferencia > 0:
        tendencia = "crecimiento"
    elif diferencia < 0:
        tendencia = "decrecimiento"
    else:
        tendencia = "estable"
    
    return {
        "año_actual": year1,
        "año_anterior": year2,
        "ventas_actual": ventas_year1,
        "ventas_anterior": ventas_year2,
        "diferencia": diferencia,
        "porcentaje_cambio": round(porcentaje_cambio, 2),
        "tendencia": tendencia,
        "datos_detallados": {
            year1: data_year1,
            year2: data_year2
        }
    }

# ============================================================================
# ENDPOINTS ADMINISTRATIVOS
# ============================================================================

@app.get("/admin/cache/stats", tags=["admin"])
async def get_cache_stats():
    """
    📊 Estadísticas del sistema de cache
    
    Retorna estadísticas detalladas del sistema de cache incluyendo
    número de entradas, actualizaciones exitosas/fallidas, y estado general.
    """
    return await flask_request("/admin/cache/stats")

@app.get("/admin/scheduler/status", tags=["admin"])
async def get_scheduler_status():
    """
    ⏰ Estado del scheduler automático
    
    Retorna el estado actual del scheduler de actualizaciones automáticas,
    incluyendo jobs programados y empresas activas.
    """
    return await flask_request("/admin/scheduler/status")

@app.post("/admin/force-update", tags=["admin"])
async def force_update():
    """
    🔄 Forzar actualización inmediata de datos
    
    Ejecuta una actualización inmediata de los datos de ventas,
    omitiendo el cache y obteniendo información fresca de QuickBooks.
    """
    return await flask_request("/admin/force-update", method="POST")

@app.post("/admin/force-annual-update", tags=["admin"])
async def force_annual_update():
    """
    📊 Forzar actualización anual completa
    
    Ejecuta una actualización completa de todos los datos anuales,
    procesando todos los meses del año actual desde QuickBooks.
    """
    return await flask_request("/admin/force-annual-update", method="POST")

# ============================================================================
# ENDPOINTS DE SISTEMA
# ============================================================================

@app.get("/health", tags=["system"])
async def health_check():
    """
    🏥 Verificación de salud del sistema
    
    Verifica que el servidor API esté funcionando y puede comunicarse
    con el servidor Flask principal.
    """
    try:
        # Verificar conexión con el servidor Flask
        response = requests.get(f"{FLASK_BASE_URL}/", timeout=5)
        flask_status = "ok" if response.status_code == 200 else "error"
    except:
        flask_status = "disconnected"
    
    return {
        "status": "ok",
        "flask_server": flask_status,
        "flask_url": FLASK_BASE_URL,
        "api_version": "2.0.0",
        "timestamp": "2025-08-06T15:30:00"
    }

@app.get("/", tags=["system"])
async def root():
    """
    🏠 Información del API
    
    Retorna información básica sobre el API de QuickBooks Sales Reporter.
    """
    return {
        "name": "QuickBooks Sales Reporter API",
        "description": "API REST para consultar datos de ventas de QuickBooks Online",
        "version": "2.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "company": "KH LLOREDA, S.A.",
        "github": "https://github.com/jordiportal/Quickbooks",
        "endpoints": {
            "sales": [
                "GET /api/sales - Ventas del mes actual",
                "GET /api/sales/{year}/{month} - Ventas de mes específico"
            ],
            "annual": [
                "GET /api/annual - Reporte anual actual",
                "GET /api/annual/{year} - Reporte anual específico",
                "GET /api/quarterly/{year} - Reporte trimestral",
                "GET /api/comparison/{year1}/{year2} - Comparación entre años"
            ],
            "admin": [
                "GET /admin/cache/stats - Estadísticas del cache",
                "GET /admin/scheduler/status - Estado del scheduler",
                "POST /admin/force-update - Actualización forzada",
                "POST /admin/force-annual-update - Actualización anual forzada"
            ]
        }
    }

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejo personalizado de errores HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2025-08-06T15:30:00"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo de errores generales"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc),
            "status_code": 500,
            "timestamp": "2025-08-06T15:30:00"
        }
    )

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal para ejecutar el servidor"""
    parser = argparse.ArgumentParser(description="QuickBooks Sales Reporter OpenAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host para el servidor (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Puerto para el servidor (default: 8080)")
    parser.add_argument("--flask-url", default="http://localhost:5000", help="URL del servidor Flask principal")
    parser.add_argument("--reload", action="store_true", help="Habilitar recarga automática en desarrollo")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Nivel de logging")
    
    args = parser.parse_args()
    
    # Configurar URL del servidor Flask
    global FLASK_BASE_URL
    FLASK_BASE_URL = args.flask_url
    
    print(f"""
🚀 Iniciando QuickBooks Sales Reporter OpenAPI Server

📡 Configuración:
   • API Server: http://{args.host}:{args.port}
   • Flask Server: {FLASK_BASE_URL}
   • Documentación: http://{args.host}:{args.port}/docs
   • OpenAPI Spec: http://{args.host}:{args.port}/openapi.json

🔗 Para OpenWebUI:
   1. Agrega este servidor como herramienta OpenAPI
   2. URL: http://{args.host}:{args.port}
   3. Haz preguntas como: "¿Cómo van las ventas de este mes?"

📋 Endpoints principales:
   • GET /api/sales - Ventas del mes actual
   • GET /api/annual - Reporte anual completo
   • GET /api/comparison/2024/2023 - Comparar años
   • POST /admin/force-update - Actualización manual

🏢 Desarrollado por KH LLOREDA, S.A.
""")
    
    # Ejecutar servidor
    uvicorn.run(
        "openapi_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()