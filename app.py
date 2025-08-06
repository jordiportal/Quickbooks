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
                <a href="/sales" class="btn" style="margin-right: 10px;">📅 Reporte Mensual</a>
                <a href="/annual" class="btn">📊 Reporte Anual</a>
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

# Template HTML para el reporte anual
ANNUAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickBooks Online - Reporte Anual {{ annual_data.año if annual_data else '' }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
        }
        .nav-buttons {
            margin-bottom: 20px;
            text-align: center;
        }
        .nav-buttons a {
            display: inline-block;
            margin: 0 10px;
            padding: 10px 20px;
            background: #0077C5;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav-buttons a:hover {
            background: #005fa3;
        }
        .nav-buttons a.active {
            background: #28a745;
        }
        .year-nav {
            margin: 20px 0;
            text-align: center;
        }
        .year-nav a {
            margin: 0 5px;
            padding: 5px 15px;
            background: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }
        .year-nav a.current {
            background: #007bff;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .summary-card .value {
            font-size: 24px;
            font-weight: bold;
        }
        .months-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .month-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }
        .month-card h4 {
            margin: 0 0 10px 0;
            color: #495057;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .month-card .month-total {
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
        }
        .month-details {
            font-size: 14px;
            color: #6c757d;
        }
        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .bar-chart {
            display: flex;
            align-items: end;
            height: 200px;
            margin: 20px 0;
            padding: 0 10px;
        }
        .bar {
            flex: 1;
            margin: 0 2px;
            background: linear-gradient(to top, #28a745, #20c997);
            border-radius: 3px 3px 0 0;
            position: relative;
            min-height: 5px;
        }
        .bar-label {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #666;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
        }
        .footer {
            margin-top: 50px;
            padding: 30px 0;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Reporte Anual QuickBooks Online</h1>
            <p>Empresa: <strong>{{ company_id }}</strong></p>
        </div>

        <div class="nav-buttons">
            <a href="/sales">📅 Vista Mensual</a>
            <a href="/annual" class="active">📊 Vista Anual</a>
            <a href="/disconnect">🚪 Desconectar</a>
        </div>

        {% if annual_data %}
        <div class="year-nav">
            <a href="/annual/{{ annual_data.current_year - 2 }}">{{ annual_data.current_year - 2 }}</a>
            <a href="/annual/{{ annual_data.current_year - 1 }}">{{ annual_data.current_year - 1 }}</a>
            <a href="/annual/{{ annual_data.current_year }}" class="current">{{ annual_data.current_year }}</a>
            {% if annual_data.current_year < 2025 %}
            <a href="/annual/{{ annual_data.current_year + 1 }}">{{ annual_data.current_year + 1 }}</a>
            {% endif %}
        </div>

        <div class="summary-cards">
            <div class="summary-card">
                <h3>💰 Total Anual</h3>
                <div class="value">${{ "%.2f"|format(annual_data.total_anual) }}</div>
            </div>
            <div class="summary-card">
                <h3>📈 Promedio Mensual</h3>
                <div class="value">${{ "%.2f"|format(annual_data.resumen.promedio_mensual) }}</div>
            </div>
            <div class="summary-card">
                <h3>🏆 Mejor Mes</h3>
                <div class="value">{{ annual_data.resumen.mejor_mes.mes }}</div>
                <small>${{ "%.2f"|format(annual_data.resumen.mejor_mes.ventas) }}</small>
            </div>
            <div class="summary-card">
                <h3>📊 Meses con Ventas</h3>
                <div class="value">{{ annual_data.resumen.meses_con_ventas }}</div>
                <small>de {{ annual_data.meses|length }} meses</small>
            </div>
        </div>

        <div class="chart-container">
            <h3>📈 Evolución Mensual {{ annual_data.año }}</h3>
            <div class="bar-chart">
                {% for month_key, month_info in annual_data.meses.items() %}
                {% set max_value = annual_data.resumen.mejor_mes.ventas %}
                {% set height = (month_info.data.total_ventas / max_value * 180) if max_value > 0 else 5 %}
                <div class="bar" style="height: {{ height }}px;">
                    <div class="bar-label">{{ month_info.nombre[:3] }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="months-grid">
            {% for month_key, month_info in annual_data.meses.items() %}
            <div class="month-card">
                <h4>
                    <span>{{ month_info.nombre }} {{ annual_data.año }}</span>
                    <span class="month-total">${{ "%.2f"|format(month_info.data.total_ventas) }}</span>
                </h4>
                <div class="month-details">
                    <div>🧾 Recibos: {{ month_info.data.recibos_de_venta.cantidad }} (${{"%.2f"|format(month_info.data.recibos_de_venta.total)}})</div>
                    <div>🧾 Facturas: {{ month_info.data.facturas.cantidad }} (${{"%.2f"|format(month_info.data.facturas.total)}})</div>
                    <div>📅 {{ month_info.data.fecha_inicio }} al {{ month_info.data.fecha_fin }}</div>
                </div>
            </div>
            {% endfor %}
        </div>

        <p style="font-size: 12px; color: #666; text-align: center;">
            {% if annual_data.from_cache %}
            📊 Datos desde cache (actualizado: {{ annual_data.cached_at if annual_data.cached_at else 'N/A' }})
            {% else %}
            🔄 Datos en tiempo real desde QuickBooks
            {% endif %}
            {% if annual_data.cache_warning %}
            <br><span style="color: #ffc107;">⚠️ Mostrando último cache disponible (QuickBooks no accesible)</span>
            {% endif %}
        </p>

        <div style="margin-top: 20px; text-align: center;">
            <button onclick="forceAnnualUpdate()" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                🔄 Actualizar Datos Anuales
            </button>
            <button onclick="showCacheStats()" style="background: #17a2b8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                📊 Ver Estadísticas
            </button>
        </div>
        {% else %}
        <div style="text-align: center; padding: 40px;">
            <h2>📊 Bienvenido al Reporte Anual</h2>
            <p>No hay datos disponibles para mostrar.</p>
        </div>
        {% endif %}

        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}
    </div>

    <footer class="footer">
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
        function forceAnnualUpdate() {
            const button = event.target;
            button.textContent = '🔄 Actualizando...';
            button.disabled = true;
            
            fetch('/admin/force-annual-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Actualización anual completada');
                    window.location.reload();
                } else {
                    alert('❌ Error en actualización: ' + (data.error || 'Error desconocido'));
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error);
            })
            .finally(() => {
                button.textContent = '🔄 Actualizar Datos Anuales';
                button.disabled = false;
            });
        }
        
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
@app.route('/sales/<int:year>/<int:month>')
def sales(year=None, month=None):
    """Obtiene y muestra el reporte de ventas del mes"""
    if 'access_token' not in session:
        return redirect('/')
    
    company_id = session['company_id']
    
    # Si no se especifica año/mes, usar mes actual
    if not year or not month:
        current_date = datetime.now()
        year = year or current_date.year
        month = month or current_date.month
    
    try:
        # Intentar obtener datos del cache primero
        period = f"{month:02d}/{year}"
        cached_data = cache_service.get_cached_sales(company_id, period)
        
        if cached_data and cached_data.get('update_success'):
            # Usar datos del cache
            sales_data = cached_data
            sales_data['from_cache'] = True
        else:
            # Si no hay cache o falló, obtener datos frescos de QuickBooks
            qb_client.access_token = session['access_token']
            qb_client.refresh_token = session['refresh_token']
            qb_client.company_id = company_id
            
            sales_data = qb_client.get_monthly_sales_summary(year, month)
            sales_data['from_cache'] = False
            
            # Actualizar cache con los nuevos datos
            cache_service.update_sales_cache(company_id, sales_data)
        
        # Agregar información de navegación
        sales_data['current_year'] = year
        sales_data['current_month'] = month
        
        return render_template_string(
            MAIN_TEMPLATE,
            authenticated=True,
            company_id=company_id,
            sales_data=sales_data,
            view_type='monthly'
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

@app.route('/annual')
@app.route('/annual/<int:year>')
def annual_sales(year=None):
    """Obtiene y muestra el reporte anual de ventas"""
    if 'access_token' not in session:
        return redirect('/')
    
    company_id = session['company_id']
    
    # Si no se especifica año, usar año actual
    if not year:
        year = datetime.now().year
    
    try:
        # Intentar obtener datos del cache anual primero
        annual_data = cache_service.get_annual_cached_data(company_id, year)
        
        if not annual_data:
            # Si no hay cache, obtener datos frescos de QuickBooks
            qb_client.access_token = session['access_token']
            qb_client.refresh_token = session['refresh_token']
            qb_client.company_id = company_id
            
            annual_data = qb_client.get_annual_sales_summary(year)
            annual_data['from_cache'] = False
            
            # Actualizar cache anual
            cache_service.update_annual_cache(company_id, year, qb_client)
        else:
            annual_data['from_cache'] = True
        
        # Agregar información de navegación
        annual_data['current_year'] = year
        
        return render_template_string(
            ANNUAL_TEMPLATE,
            authenticated=True,
            company_id=company_id,
            annual_data=annual_data,
            view_type='annual'
        )
        
    except Exception as e:
        # Si falla todo, intentar mostrar último cache disponible
        annual_data = cache_service.get_annual_cached_data(company_id, year)
        if annual_data:
            annual_data['from_cache'] = True
            annual_data['cache_warning'] = True
            return render_template_string(
                ANNUAL_TEMPLATE,
                authenticated=True,
                company_id=company_id,
                annual_data=annual_data,
                view_type='annual',
                error=f"Error conectando con QuickBooks (mostrando datos en cache): {str(e)}"
            )
        else:
            return render_template_string(
                MAIN_TEMPLATE,
                authenticated=True,
                company_id=company_id,
                view_type='annual',
                error=f"Error obteniendo datos anuales: {str(e)}"
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

@app.route('/admin/force-annual-update', methods=['POST'])
def force_annual_update():
    """Endpoint para forzar actualización anual completa"""
    if 'company_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    try:
        company_id = session['company_id']
        year = datetime.now().year
        
        # Configurar cliente QuickBooks
        qb_client.access_token = session['access_token']
        qb_client.refresh_token = session['refresh_token']
        qb_client.company_id = company_id
        
        # Actualizar cache anual
        success = cache_service.update_annual_cache(company_id, year, qb_client)
        
        return jsonify({
            'success': success,
            'company_id': company_id,
            'year': year,
            'timestamp': datetime.now().isoformat()
        })
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