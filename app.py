"""
Aplicación Flask para conectar con QuickBooks Online y mostrar ventas del mes
"""

import os
import atexit
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string, jsonify, render_template
from quickbooks_client import QuickBooksClient
from sales_cache import cache_service
from scheduler import sales_scheduler
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')

# Instancia global del cliente de QuickBooks
qb_client = QuickBooksClient()

# Iniciar scheduler automático
sales_scheduler.start()

# Registrar shutdown del scheduler
atexit.register(lambda: sales_scheduler.stop())

# Template HTML para la página principal
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickBooks Online - Ventas del Mes</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c5aa0;
            text-align: center;
            margin-bottom: 30px;
        }
        .auth-section {
            text-align: center;
            padding: 40px;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #0077C5;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #005a94;
        }
        .sales-summary {
            background: #e8f5e8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .metric {
            display: inline-block;
            background: white;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            min-width: 150px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c5aa0;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 QuickBooks Online - Reporte de Ventas</h1>
        
        {% if not authenticated %}
        <div class="auth-section">
            <h2>Conectar con QuickBooks Online</h2>
            <p>Para ver el reporte de ventas del mes, necesitas autorizar el acceso a tu cuenta de QuickBooks Online.</p>
            <a href="/auth" class="btn">🔗 Conectar con QuickBooks</a>
        </div>
        {% else %}
        <div class="sales-summary">
            <h2>✅ Conectado a QuickBooks Online</h2>
            <p>Company ID: {{ company_id }}</p>
            
            <div style="margin: 20px 0;">
                <a href="/sales" class="btn">📈 Ver Ventas del Mes</a>
                <a href="/disconnect" class="btn" style="background: #dc3545; margin-left: 10px;">🔌 Desconectar</a>
            </div>
        </div>
        {% endif %}
        
        {% if sales_data %}
        <div class="sales-summary">
            <h2>💰 Resumen de Ventas - {{ sales_data.período }}</h2>
            
            <div style="text-align: center; margin: 20px 0;">
                <div class="metric">
                    <div class="metric-value">${{ "%.2f"|format(sales_data.total_ventas) }}</div>
                    <div class="metric-label">Total Ventas</div>
                </div>
                
                <div class="metric">
                    <div class="metric-value">{{ sales_data.recibos_de_venta.cantidad }}</div>
                    <div class="metric-label">Recibos de Venta</div>
                </div>
                
                <div class="metric">
                    <div class="metric-value">{{ sales_data.facturas.cantidad }}</div>
                    <div class="metric-label">Facturas</div>
                </div>
            </div>
            
            <h3>Detalle por Tipo de Transacción</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <tr style="background: #f1f1f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Tipo</th>
                    <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Cantidad</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Total</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">Recibos de Venta</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{{ sales_data.recibos_de_venta.cantidad }}</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">${{ "%.2f"|format(sales_data.recibos_de_venta.total) }}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">Facturas</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{{ sales_data.facturas.cantidad }}</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">${{ "%.2f"|format(sales_data.facturas.total) }}</td>
                </tr>
                <tr style="background: #f1f1f1; font-weight: bold;">
                    <td style="padding: 10px; border: 1px solid #ddd;">TOTAL</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{{ sales_data.recibos_de_venta.cantidad + sales_data.facturas.cantidad }}</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">${{ "%.2f"|format(sales_data.total_ventas) }}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                Período: {{ sales_data.fecha_inicio }} al {{ sales_data.fecha_fin }}
                {% if sales_data.from_cache %}
                <br><span style="color: #28a745;">📊 Datos desde cache (actualizado: {{ sales_data.last_updated }})</span>
                {% else %}
                <br><span style="color: #007bff;">🔄 Datos en tiempo real desde QuickBooks</span>
                {% endif %}
                {% if sales_data.cache_warning %}
                <br><span style="color: #ffc107;">⚠️ Mostrando último cache disponible (QuickBooks no accesible)</span>
                {% endif %}
            </p>
            
            {% if authenticated %}
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="forceUpdate()" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                    🔄 Forzar Actualización
                </button>
                <button onclick="showCacheStats()" style="background: #17a2b8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    📊 Ver Estadísticas
                </button>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}
    </div>
    
    <!-- Pie de página con enlaces legales -->
    <footer style="margin-top: 50px; padding: 30px 0; background: #f8f9fa; border-top: 1px solid #ddd;">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center;">
            <div style="margin-bottom: 20px;">
                <p style="margin: 0; color: #666; font-size: 14px;">
                    <strong>KH LLOREDA, S.A.</strong><br>
                    Passeig de la Ribera, 111 8420 P. I. Can Castells CANOVELLES<br>
                    Tel: 938492633 | Email: lopd@khlloreda.com
                </p>
            </div>
            <div style="margin-bottom: 15px;">
                <a href="/terms" style="color: #0077C5; text-decoration: none; margin: 0 15px; font-size: 13px;">Términos y Condiciones</a>
                <span style="color: #ccc;">|</span>
                <a href="/privacy" style="color: #0077C5; text-decoration: none; margin: 0 15px; font-size: 13px;">Política de Privacidad</a>
            </div>
            <p style="margin: 0; color: #999; font-size: 12px;">
                © 2024 KH LLOREDA, S.A. Todos los derechos reservados.<br>
                NIF: A58288598 | Registro Mercantil de Barcelona, Tomo 8062, Folio 091, Hoja 92596
            </p>
        </div>
    </footer>
    
    <script>
        // Auto-refresh de datos cada 30 segundos si estamos autenticados
        {% if authenticated and not sales_data %}
        setTimeout(function() {
            window.location.href = '/sales';
        }, 2000);
        {% endif %}
        
        // Función para forzar actualización
        function forceUpdate() {
            const button = event.target;
            button.textContent = '🔄 Actualizando...';
            button.disabled = true;
            
            fetch('/admin/force-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Actualización completada');
                    window.location.reload();
                } else {
                    alert('❌ Error en actualización: ' + (data.error || 'Error desconocido'));
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error);
            })
            .finally(() => {
                button.textContent = '🔄 Forzar Actualización';
                button.disabled = false;
            });
        }
        
        // Función para mostrar estadísticas del cache
        function showCacheStats() {
            Promise.all([
                fetch('/admin/cache/stats').then(r => r.json()),
                fetch('/admin/scheduler/status').then(r => r.json())
            ])
            .then(([cacheStats, schedulerStatus]) => {
                let message = `📊 ESTADÍSTICAS DEL SISTEMA\\n\\n`;
                message += `Cache:\\n`;
                message += `- Total entradas: ${cacheStats.total_entries}\\n`;
                message += `- Actualizaciones exitosas: ${cacheStats.successful_updates}\\n`;
                message += `- Actualizaciones fallidas: ${cacheStats.failed_updates}\\n`;
                message += `- Última actualización: ${cacheStats.latest_update || 'N/A'}\\n\\n`;
                message += `Scheduler:\\n`;
                message += `- Estado: ${schedulerStatus.scheduler_running ? 'Activo' : 'Inactivo'}\\n`;
                message += `- Empresas activas: ${schedulerStatus.active_companies}\\n`;
                message += `- Jobs programados: ${schedulerStatus.jobs.length}`;
                
                alert(message);
            })
            .catch(error => {
                alert('❌ Error obteniendo estadísticas: ' + error);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    authenticated = 'access_token' in session
    company_id = session.get('company_id')
    
    return render_template_string(
        MAIN_TEMPLATE,
        authenticated=authenticated,
        company_id=company_id
    )

@app.route('/auth')
def auth():
    """Inicia el proceso de autenticación con QuickBooks"""
    auth_url = qb_client.get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Maneja el callback de autenticación de QuickBooks"""
    code = request.args.get('code')
    realm_id = request.args.get('realmId')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        return render_template_string(
            MAIN_TEMPLATE,
            error=f"Error de autorización: {error}"
        )
    
    if not code or not realm_id:
        return render_template_string(
            MAIN_TEMPLATE,
            error="Faltan parámetros de autorización"
        )
    
    # Intercambiar código por tokens
    success = qb_client.exchange_code_for_tokens(code, realm_id)
    
    if success:
        # Guardar tokens en la sesión
        session['access_token'] = qb_client.access_token
        session['refresh_token'] = qb_client.refresh_token
        session['company_id'] = qb_client.company_id
        
        # Registrar empresa para actualizaciones automáticas
        sales_scheduler.register_company(
            company_id=qb_client.company_id,
            access_token=qb_client.access_token,
            refresh_token=qb_client.refresh_token
        )
        
        return redirect('/')
    else:
        return render_template_string(
            MAIN_TEMPLATE,
            error="Error al obtener tokens de acceso"
        )

@app.route('/sales')
def sales():
    """Obtiene y muestra el reporte de ventas del mes"""
    if 'access_token' not in session:
        return redirect('/')
    
    company_id = session['company_id']
    
    try:
        # Intentar obtener datos del cache primero
        cached_data = cache_service.get_cached_sales(company_id)
        
        if cached_data and cached_data.get('update_success'):
            # Usar datos del cache
            sales_data = cached_data
            sales_data['from_cache'] = True
        else:
            # Si no hay cache o falló, obtener datos frescos de QuickBooks
            qb_client.access_token = session['access_token']
            qb_client.refresh_token = session['refresh_token']
            qb_client.company_id = company_id
            
            sales_data = qb_client.get_monthly_sales_summary()
            sales_data['from_cache'] = False
            
            # Actualizar cache con los nuevos datos
            cache_service.update_sales_cache(company_id, sales_data)
        
        return render_template_string(
            MAIN_TEMPLATE,
            authenticated=True,
            company_id=company_id,
            sales_data=sales_data
        )
        
    except Exception as e:
        # Si falla todo, intentar mostrar último cache disponible
        cached_data = cache_service.get_cached_sales(company_id)
        if cached_data:
            cached_data['from_cache'] = True
            cached_data['cache_warning'] = True
            return render_template_string(
                MAIN_TEMPLATE,
                authenticated=True,
                company_id=company_id,
                sales_data=cached_data,
                error=f"Error conectando con QuickBooks (mostrando datos en cache): {str(e)}"
            )
        else:
            return render_template_string(
                MAIN_TEMPLATE,
                authenticated=True,
                company_id=company_id,
                error=f"Error obteniendo datos de ventas: {str(e)}"
            )

@app.route('/api/sales')
def api_sales():
    """API endpoint para obtener datos de ventas en formato JSON"""
    if 'access_token' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    # Restaurar tokens en el cliente
    qb_client.access_token = session['access_token']
    qb_client.refresh_token = session['refresh_token']
    qb_client.company_id = session['company_id']
    
    try:
        sales_data = qb_client.get_monthly_sales_summary()
        return jsonify(sales_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/disconnect')
def disconnect():
    """Desconecta la sesión actual"""
    # Desregistrar empresa del scheduler si está en sesión
    if 'company_id' in session:
        sales_scheduler.unregister_company(session['company_id'])
    
    session.clear()
    qb_client.access_token = None
    qb_client.refresh_token = None
    qb_client.company_id = None
    
    return redirect('/')

@app.route('/admin/cache/stats')
def cache_stats():
    """Endpoint para ver estadísticas del cache"""
    if 'company_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        stats = cache_service.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/scheduler/status')
def scheduler_status():
    """Endpoint para ver estado del scheduler"""
    if 'company_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        status = sales_scheduler.get_jobs_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/force-update', methods=['POST'])
def force_update():
    """Endpoint para forzar actualización inmediata"""
    if 'company_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        company_id = session['company_id']
        result = sales_scheduler.force_update(company_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/cache/history')
def cache_history():
    """Endpoint para ver historial de cache"""
    if 'company_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        company_id = session['company_id']
        history = cache_service.get_all_cached_periods(company_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/terms')
def terms():
    """Página de términos y condiciones"""
    try:
        with open('templates/terminos.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar variables de plantilla
        content = content.replace('{{ fecha_actual }}', datetime.now().strftime('%d de %B de %Y'))
        content = content.replace('{{ año_actual }}', str(datetime.now().year))
        
        return content
    except FileNotFoundError:
        return render_template_string("""
        <h1>Términos y Condiciones</h1>
        <p>Página en construcción. Por favor contacte con el administrador.</p>
        <a href="/">Volver</a>
        """)

@app.route('/privacy')
def privacy():
    """Página de política de privacidad"""
    try:
        with open('templates/privacidad.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar variables de plantilla
        content = content.replace('{{ fecha_actual }}', datetime.now().strftime('%d de %B de %Y'))
        content = content.replace('{{ año_actual }}', str(datetime.now().year))
        
        return content
    except FileNotFoundError:
        return render_template_string("""
        <h1>Política de Privacidad</h1>
        <p>Página en construcción. Por favor contacte con el administrador.</p>
        <a href="/">Volver</a>
        """)

if __name__ == '__main__':
    print("🚀 Iniciando aplicación QuickBooks Online...")
    print("📋 Pasos para configurar:")
    print("1. Crea una aplicación en https://developer.intuit.com/")
    print("2. Copia config.env.example a .env y configura tus credenciales")
    print("3. Instala dependencias: pip install -r requirements.txt")
    print("4. Visita http://localhost:5000 para comenzar")
    print()
    
    app.run(debug=True, port=5000)