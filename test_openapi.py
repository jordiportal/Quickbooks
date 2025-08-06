#!/usr/bin/env python3
"""
Script de prueba para el servidor OpenAPI de QuickBooks Sales Reporter

Este script verifica que todos los endpoints estén funcionando correctamente
y proporciona ejemplos de cómo usar la API desde OpenWebUI.

Uso:
    python test_openapi.py
    python test_openapi.py --server http://localhost:8080
"""

import requests
import argparse
import json
import sys
from datetime import datetime
import time

class OpenAPITester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
        
    def test_endpoint(self, method, endpoint, description, expected_status=200, **kwargs):
        """Prueba un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n🧪 {description}")
        print(f"   {method} {endpoint}")
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=30, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, timeout=30, **kwargs)
            else:
                response = self.session.request(method, url, timeout=30, **kwargs)
            
            response_time = time.time() - start_time
            
            # Verificar status code
            status_ok = response.status_code == expected_status
            status_symbol = "✅" if status_ok else "❌"
            
            print(f"   {status_symbol} Status: {response.status_code} ({response_time:.2f}s)")
            
            # Mostrar contenido de respuesta
            if response.status_code < 400:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        # Mostrar campos principales
                        key_fields = ['total_ventas', 'año', 'período', 'status', 'name', 'total_anual']
                        for field in key_fields:
                            if field in data:
                                print(f"   📊 {field}: {data[field]}")
                        
                        # Mostrar estructura si es compleja
                        if 'meses' in data:
                            print(f"   📅 Meses disponibles: {len(data['meses'])}")
                        if 'resumen' in data:
                            print(f"   📈 Incluye resumen analítico")
                    else:
                        print(f"   📄 Respuesta: {str(data)[:100]}...")
                        
                except json.JSONDecodeError:
                    print(f"   📄 Respuesta texto: {response.text[:100]}...")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Guardar resultado
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'success': status_ok,
                'response_time': response_time,
                'description': description
            })
            
            return response
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - El endpoint puede estar procesando datos")
            self.results.append({
                'endpoint': endpoint,
                'method': method, 
                'status_code': 'timeout',
                'success': False,
                'response_time': 30,
                'description': description
            })
            return None
            
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Error de conexión - ¿Está el servidor ejecutándose?")
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': 'connection_error', 
                'success': False,
                'response_time': 0,
                'description': description
            })
            return None
            
        except Exception as e:
            print(f"   💥 Error inesperado: {e}")
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': 'error',
                'success': False, 
                'response_time': 0,
                'description': description
            })
            return None
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas de endpoints"""
        
        print(f"""
🚀 Iniciando pruebas del QuickBooks Sales Reporter OpenAPI
📡 Servidor: {self.base_url}
⏰ Tiempo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        # ============================================================================
        # PRUEBAS BÁSICAS
        # ============================================================================
        
        print("\n" + "="*60)
        print("📋 PRUEBAS BÁSICAS DEL SISTEMA")
        print("="*60)
        
        self.test_endpoint("GET", "/", "Información básica del API")
        self.test_endpoint("GET", "/health", "Health check del sistema")
        
        # ============================================================================
        # PRUEBAS DE VENTAS MENSUALES
        # ============================================================================
        
        print("\n" + "="*60)
        print("📊 PRUEBAS DE VENTAS MENSUALES")
        print("="*60)
        
        self.test_endpoint("GET", "/api/sales", "Ventas del mes actual")
        
        # Probar mes específico
        current_year = datetime.now().year
        self.test_endpoint("GET", f"/api/sales/{current_year}/8", "Ventas de agosto 2025")
        self.test_endpoint("GET", f"/api/sales/2024/7", "Ventas de julio 2024")
        
        # Probar parámetros inválidos
        self.test_endpoint("GET", "/api/sales/2019/1", "Año inválido (debe fallar)", expected_status=400)
        self.test_endpoint("GET", "/api/sales/2024/13", "Mes inválido (debe fallar)", expected_status=400)
        
        # ============================================================================
        # PRUEBAS DE REPORTES ANUALES
        # ============================================================================
        
        print("\n" + "="*60)
        print("📈 PRUEBAS DE REPORTES ANUALES")
        print("="*60)
        
        self.test_endpoint("GET", "/api/annual", "Reporte anual del año actual")
        self.test_endpoint("GET", "/api/annual/2024", "Reporte anual de 2024")
        self.test_endpoint("GET", "/api/quarterly/2024", "Reporte trimestral de 2024")
        
        # Comparación entre años
        self.test_endpoint("GET", "/api/comparison/2024/2023", "Comparación 2024 vs 2023")
        
        # Año inválido
        self.test_endpoint("GET", "/api/annual/2019", "Año inválido (debe fallar)", expected_status=400)
        
        # ============================================================================
        # PRUEBAS ADMINISTRATIVAS
        # ============================================================================
        
        print("\n" + "="*60)
        print("🛠️ PRUEBAS ADMINISTRATIVAS")
        print("="*60)
        
        # Nota: Estos pueden fallar si no hay autenticación
        self.test_endpoint("GET", "/admin/cache/stats", "Estadísticas del cache", expected_status=401)
        self.test_endpoint("GET", "/admin/scheduler/status", "Estado del scheduler", expected_status=401)
        
        # ============================================================================
        # PRUEBAS DE DOCUMENTACIÓN
        # ============================================================================
        
        print("\n" + "="*60)
        print("📚 PRUEBAS DE DOCUMENTACIÓN")
        print("="*60)
        
        self.test_endpoint("GET", "/docs", "Swagger UI", expected_status=200)
        self.test_endpoint("GET", "/openapi.json", "Especificación OpenAPI", expected_status=200)
        self.test_endpoint("GET", "/redoc", "ReDoc UI", expected_status=200)
        
    def print_summary(self):
        """Imprime resumen de resultados"""
        
        successful = len([r for r in self.results if r['success']])
        total = len(self.results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*60)
        
        print(f"✅ Exitosas: {successful}/{total} ({success_rate:.1f}%)")
        print(f"❌ Fallidas: {total - successful}/{total}")
        
        # Mostrar fallos
        failures = [r for r in self.results if not r['success']]
        if failures:
            print(f"\n❌ Endpoints que fallaron:")
            for failure in failures:
                status = failure['status_code']
                print(f"   • {failure['method']} {failure['endpoint']} → {status}")
        
        # Mostrar endpoints más lentos
        slow_endpoints = sorted([r for r in self.results if r['success'] and isinstance(r['response_time'], (int, float))], 
                               key=lambda x: x['response_time'], reverse=True)[:3]
        
        if slow_endpoints:
            print(f"\n⏰ Endpoints más lentos:")
            for endpoint in slow_endpoints:
                print(f"   • {endpoint['method']} {endpoint['endpoint']} → {endpoint['response_time']:.2f}s")
        
        # Consejos
        print(f"\n💡 Consejos:")
        if success_rate < 50:
            print("   • Verifica que el servidor Flask esté ejecutándose en localhost:5000")
            print("   • Asegúrate de haber autorizado QuickBooks en localhost:5000/auth")
        elif success_rate < 80:
            print("   • Algunos endpoints requieren autenticación previa")
            print("   • Los timeouts pueden indicar procesamiento de datos anuales")
        else:
            print("   • ¡El sistema está funcionando correctamente!")
            print("   • Puedes conectarlo con OpenWebUI usando la URL del servidor")
        
        print(f"\n🔗 Para conectar con OpenWebUI:")
        print(f"   • URL del servidor: {self.base_url}")
        print(f"   • Documentación: {self.base_url}/docs")
        print(f"   • Health check: {self.base_url}/health")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Pruebas del OpenAPI Server de QuickBooks")
    parser.add_argument("--server", default="http://localhost:8080", 
                       help="URL del servidor OpenAPI (default: http://localhost:8080)")
    parser.add_argument("--endpoint", help="Probar solo un endpoint específico")
    parser.add_argument("--verbose", action="store_true", help="Mostrar respuestas completas")
    
    args = parser.parse_args()
    
    # Crear tester
    tester = OpenAPITester(args.server)
    
    if args.endpoint:
        # Probar endpoint específico
        tester.test_endpoint("GET", args.endpoint, f"Prueba de {args.endpoint}")
    else:
        # Ejecutar todas las pruebas
        tester.run_all_tests()
    
    # Mostrar resumen
    tester.print_summary()
    
    # Exit code basado en resultados
    success_rate = len([r for r in tester.results if r['success']]) / len(tester.results) * 100
    sys.exit(0 if success_rate >= 80 else 1)

if __name__ == "__main__":
    main()