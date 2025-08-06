"""
Ejemplo de uso directo del cliente de QuickBooks Online
Este script muestra cómo obtener ventas del mes sin interfaz web
"""

import json
from datetime import datetime
from quickbooks_client import QuickBooksClient

def main():
    """Función principal del ejemplo"""
    print("=== Cliente QuickBooks Online - Ejemplo de Ventas ===\n")
    
    # Crear instancia del cliente
    qb = QuickBooksClient()
    
    # Verificar configuración
    if not qb.client_id or not qb.client_secret:
        print("❌ Error: Faltan credenciales de QuickBooks")
        print("   Configura QB_CLIENT_ID y QB_CLIENT_SECRET en tu archivo .env")
        return
    
    print("✅ Credenciales configuradas")
    print(f"   Client ID: {qb.client_id[:10]}...")
    print(f"   Redirect URI: {qb.redirect_uri}")
    print()
    
    # Mostrar URL de autorización
    auth_url = qb.get_auth_url()
    print("🔗 URL de autorización de QuickBooks:")
    print(f"   {auth_url}")
    print()
    print("📋 Pasos para autorizar:")
    print("1. Visita la URL de arriba en tu navegador")
    print("2. Autoriza el acceso a tu cuenta de QuickBooks")
    print("3. Copia el 'code' y 'realmId' de la URL de callback")
    print("4. Ejecuta este script con esos parámetros")
    print()
    
    # En un uso real, aquí tendrías el código de autorización
    # Por ahora, mostramos cómo sería el proceso
    
    print("💡 Ejemplo de uso con tokens obtenidos:")
    print()
    
    # Simular datos de ejemplo (en uso real, estos vendrían de la API)
    ejemplo_resumen = {
        'período': f"{datetime.now().month:02d}/{datetime.now().year}",
        'fecha_inicio': datetime.now().replace(day=1).strftime('%Y-%m-%d'),
        'fecha_fin': datetime.now().strftime('%Y-%m-%d'),
        'recibos_de_venta': {
            'cantidad': 15,
            'total': 12500.75
        },
        'facturas': {
            'cantidad': 8,
            'total': 8750.25
        },
        'total_ventas': 21251.00
    }
    
    print("📊 Ejemplo de resumen de ventas:")
    print(json.dumps(ejemplo_resumen, indent=2, ensure_ascii=False))
    print()
    
    print("🔧 Para usar con datos reales:")
    print("1. Ejecuta 'python app.py' para la interfaz web completa")
    print("2. O implementa el flujo de autorización en este script")
    print()

def ejemplo_con_tokens(access_token: str, company_id: str):
    """
    Ejemplo de uso cuando ya tienes tokens válidos
    Args:
        access_token: Token de acceso válido
        company_id: ID de la compañía
    """
    qb = QuickBooksClient()
    qb.access_token = access_token
    qb.company_id = company_id
    
    print("🔄 Obteniendo ventas del mes actual...")
    
    try:
        # Obtener resumen de ventas
        resumen = qb.get_monthly_sales_summary()
        
        print("✅ Datos obtenidos exitosamente:")
        print(f"📅 Período: {resumen['período']}")
        print(f"💰 Total de ventas: ${resumen['total_ventas']:,.2f}")
        print(f"🧾 Recibos de venta: {resumen['recibos_de_venta']['cantidad']}")
        print(f"📄 Facturas: {resumen['facturas']['cantidad']}")
        print()
        
        # Mostrar detalles si hay transacciones
        if resumen['recibos_de_venta']['cantidad'] > 0:
            print("📋 Detalles de recibos de venta:")
            for i, recibo in enumerate(resumen['detalle_transacciones']['recibos'][:5], 1):
                fecha = recibo.get('TxnDate', 'N/A')
                total = float(recibo.get('TotalAmt', 0))
                print(f"   {i}. Fecha: {fecha}, Total: ${total:.2f}")
            if len(resumen['detalle_transacciones']['recibos']) > 5:
                print(f"   ... y {len(resumen['detalle_transacciones']['recibos']) - 5} más")
            print()
        
        if resumen['facturas']['cantidad'] > 0:
            print("📋 Detalles de facturas:")
            for i, factura in enumerate(resumen['detalle_transacciones']['facturas'][:5], 1):
                fecha = factura.get('TxnDate', 'N/A')
                total = float(factura.get('TotalAmt', 0))
                print(f"   {i}. Fecha: {fecha}, Total: ${total:.2f}")
            if len(resumen['detalle_transacciones']['facturas']) > 5:
                print(f"   ... y {len(resumen['detalle_transacciones']['facturas']) - 5} más")
            print()
        
        return resumen
        
    except Exception as e:
        print(f"❌ Error obteniendo datos: {str(e)}")
        return None

if __name__ == "__main__":
    main()
    
    # Descomenta y modifica las siguientes líneas si tienes tokens válidos:
    # ACCESS_TOKEN = "tu_access_token_aquí"
    # COMPANY_ID = "tu_company_id_aquí"
    # ejemplo_con_tokens(ACCESS_TOKEN, COMPANY_ID)