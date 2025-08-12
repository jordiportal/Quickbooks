#!/usr/bin/env python3
"""
🚀 Test completo del setup actualizado
Inicia Flask + FastAPI y prueba la compatibilidad con OpenWebUI
"""

import subprocess
import time
import requests
import json
import sys
import os
from threading import Thread

def start_flask_server():
    """Iniciar servidor Flask en background"""
    try:
        print("🌐 Iniciando servidor Flask...")
        os.environ['FLASK_ENV'] = 'development'
        subprocess.run([sys.executable, 'app.py'], check=True)
    except Exception as e:
        print(f"❌ Error iniciando Flask: {e}")

def start_fastapi_server():
    """Iniciar servidor FastAPI en background"""
    try:
        print("🚀 Iniciando servidor FastAPI...")
        subprocess.run([sys.executable, 'openapi_server.py', '--host', '0.0.0.0', '--port', '8080'], check=True)
    except Exception as e:
        print(f"❌ Error iniciando FastAPI: {e}")

def test_servers():
    """Probar que ambos servidores respondan"""
    
    print("\n🔍 PROBANDO SERVIDORES...")
    
    # Esperar a que los servidores se inicien
    print("⏳ Esperando servidores...")
    time.sleep(5)
    
    # Probar Flask
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask (puerto 5000): OK")
        else:
            print(f"⚠️ Flask (puerto 5000): {response.status_code}")
    except Exception as e:
        print(f"❌ Flask (puerto 5000): {e}")
    
    # Probar FastAPI
    try:
        response = requests.get("http://localhost:8080/openapi.json", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI (puerto 8080): OK")
        else:
            print(f"⚠️ FastAPI (puerto 8080): {response.status_code}")
    except Exception as e:
        print(f"❌ FastAPI (puerto 8080): {e}")

def test_schema_endpoints():
    """Probar los endpoints del esquema actualizado"""
    
    print("\n📊 PROBANDO ESQUEMA ACTUALIZADO...")
    
    try:
        # Probar esquema desde FastAPI
        response = requests.get("http://localhost:8080/api/schema", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            tables = schema.get('tables', {})
            
            print(f"✅ Esquema obtenido - {len(tables)} tablas:")
            for table_name in tables:
                print(f"   📋 {table_name}")
            
            # Verificar nuevos campos en sales_cache
            sales_cache = tables.get('sales_cache', {}).get('columns', {})
            new_fields = ['total_units', 'unique_customers', 'unique_products']
            found = [f for f in new_fields if f in sales_cache]
            
            print(f"✅ Nuevos campos encontrados: {found}")
            
            return True
        else:
            print(f"❌ Error obteniendo esquema: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando esquema: {e}")
        return False

def test_sql_queries():
    """Probar consultas SQL básicas"""
    
    print("\n🔍 PROBANDO CONSULTAS SQL...")
    
    queries = [
        {
            "name": "Estructura sales_cache",
            "sql": "SELECT COUNT(*) as total_records FROM sales_cache"
        },
        {
            "name": "Verificar nuevos campos",
            "sql": "SELECT period, total_sales, total_units, unique_customers, unique_products FROM sales_cache LIMIT 1"
        },
        {
            "name": "Contar productos",
            "sql": "SELECT COUNT(*) as product_records FROM product_sales"
        },
        {
            "name": "Contar clientes", 
            "sql": "SELECT COUNT(*) as customer_records FROM customer_sales"
        }
    ]
    
    for query in queries:
        try:
            response = requests.post(
                "http://localhost:8080/api/query/sql",
                json={"sql": query["sql"]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {query['name']}: {result.get('row_count', 0)} filas")
                else:
                    print(f"⚠️ {query['name']}: {result.get('error', 'Sin error')}")
            else:
                print(f"❌ {query['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {query['name']}: {e}")

def create_summary():
    """Crear resumen final para el usuario"""
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE ACTUALIZACIONES PARA OPENWEBUI")
    print("=" * 60)
    
    print("\n✅ CAMBIOS IMPLEMENTADOS:")
    print("   📊 sales_cache ahora incluye:")
    print("      - total_units: Total de unidades vendidas")
    print("      - unique_customers: Número de clientes únicos")
    print("      - unique_products: Número de productos únicos")
    print()
    print("   📦 Nueva tabla product_sales:")
    print("      - Ventas detalladas por producto y período")
    print("      - Incluye unidades, precios promedio, clientes únicos")
    print()
    print("   👥 Nueva tabla customer_sales:")
    print("      - Ventas detalladas por cliente y período")
    print("      - Incluye unidades totales, productos únicos")
    print()
    
    print("🔗 URLS PARA OPENWEBUI:")
    print("   🌐 Servidor principal: http://localhost:8080")
    print("   📋 Esquema de BD: http://localhost:8080/api/schema")
    print("   🧠 Consultas SQL: http://localhost:8080/api/query/sql")
    print("   📖 Documentación: http://localhost:8080/docs")
    print()
    
    print("💡 EJEMPLOS DE PREGUNTAS PARA OPENWEBUI:")
    print("   • ¿Cuáles son los 5 productos más vendidos por unidades?")
    print("   • ¿Qué clientes han comprado más este año?")
    print("   • Muestra las ventas totales y unidades por mes en 2025")
    print("   • ¿Cuál es el producto más rentable?")
    print("   • ¿Qué clientes son más fieles (compran cada mes)?")
    print("   • Compara las ventas por trimestre")
    print()
    
    print("🛠️ CONFIGURACIÓN EN OPENWEBUI:")
    print("   1. Agregar nueva herramienta (tool)")
    print("   2. URL: http://localhost:8080")
    print("   3. Tipo: OpenAPI/Swagger")
    print("   4. El esquema se cargará automáticamente")
    print()
    
    print("🔄 ACTUALIZACIÓN DE DATOS:")
    print("   • Los datos se actualizan automáticamente cada hora")
    print("   • Para forzar actualización: POST /admin/force-update")
    print("   • Los nuevos campos se llenan en la próxima actualización")

if __name__ == "__main__":
    print("🚀 INICIANDO TEST COMPLETO DEL SETUP ACTUALIZADO")
    print("=" * 60)
    
    # Solo hacer tests directos sin iniciar servidores
    # (ya que el usuario puede tener procesos corriendo)
    
    print("📋 VERIFICANDO ESTADO ACTUAL...")
    
    # Probar si los servidores ya están corriendo
    flask_running = False
    fastapi_running = False
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        flask_running = response.status_code == 200
        print("✅ Flask ya está corriendo")
    except:
        print("⚠️ Flask no está corriendo")
    
    try:
        response = requests.get("http://localhost:8080/openapi.json", timeout=2)
        fastapi_running = response.status_code == 200
        print("✅ FastAPI ya está corriendo")
    except:
        print("⚠️ FastAPI no está corriendo")
    
    if fastapi_running:
        schema_ok = test_schema_endpoints()
        if schema_ok:
            test_sql_queries()
    else:
        print("\n💡 Para probar completamente:")
        print("   1. Ejecuta: python app.py (en una terminal)")
        print("   2. Ejecuta: python openapi_server.py --host 0.0.0.0 --port 8080 (en otra terminal)")
        print("   3. Luego ejecuta: python test_complete_setup.py")
    
    create_summary()
