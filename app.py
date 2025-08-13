"""
Aplicación Flask para conectar con QuickBooks Online y mostrar ventas del mes
"""

import os
import atexit
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string, jsonify, render_template
from quickbooks_client import QuickBooksClient
from sales_cache import cache_service, SalesCache
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
                <a href="/annual" class="btn" style="margin-right: 10px;">📊 Reporte Anual</a>
                <a href="/detailed_annual_report" class="btn" style="margin-right: 10px;">📈 Informe Detallado</a>
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

# Template para informe anual detallado
detailed_annual_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Informe Anual Detallado {{ year }} - QuickBooks</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(31,38,135,.37);
        }
        .year-nav {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .year-nav a {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
        }
        .year-nav a:hover { background: #0056b3; transform: translateY(-2px); }
        .year-nav a.current { background: #28a745; }
        
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(31,38,135,.37);
            border-left: 5px solid;
        }
        .metric-card.sales { border-left-color: #28a745; }
        .metric-card.units { border-left-color: #17a2b8; }
        .metric-card.transactions { border-left-color: #ffc107; }
        .metric-card.customers { border-left-color: #dc3545; }
        .metric-card.products { border-left-color: #6f42c1; }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        @media (max-width: 1200px) {
            .content-grid { grid-template-columns: 1fr; }
        }
        
        .section {
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(31,38,135,.37);
        }
        .section h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
            font-size: 1.5em;
        }
        
        .monthly-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .month-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #dee2e6;
            transition: all 0.3s ease;
        }
        .month-card:hover {
            background: #e9ecef;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .month-name {
            font-weight: bold;
            color: #495057;
            margin-bottom: 8px;
        }
        .month-value {
            font-size: 1.2em;
            color: #28a745;
        }
        .month-units {
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .top-list {
            list-style: none;
            margin: 15px 0;
        }
        .top-list li {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            transition: all 0.3s ease;
        }
        .top-list li:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .item-name {
            font-weight: 600;
            color: #495057;
        }
        .item-stats {
            text-align: right;
            font-size: 0.9em;
        }
        .item-value {
            color: #28a745;
            font-weight: bold;
        }
        .item-units {
            color: #6c757d;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        
        .filters {
            background: rgba(255,255,255,0.9);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filter-group label {
            font-weight: 600;
            color: #495057;
        }
        .filter-group select, .filter-group input {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .footer {
            background: rgba(255,255,255,0.9);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 30px;
        }
        .footer a {
            color: #007bff;
            text-decoration: none;
            margin: 0 15px;
        }
        .footer a:hover { text-decoration: underline; }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        .empty-state h4 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Informe Anual Detallado {{ year }}</h1>
            <p>Análisis completo de ventas, productos y clientes</p>
            
            <div class="year-nav">
                {% for y in range(current_year - 3, current_year + 2) %}
                    <a href="?year={{ y }}" {% if y == year %}class="current"{% endif %}>{{ y }}</a>
                {% endfor %}
            </div>
        </div>
        
        <!-- Overview Metrics -->
        <div class="overview-grid">
            <div class="metric-card sales">
                <div class="metric-value">${{ "%.2f"|format(report.totales_anuales.ventas_totales) }}</div>
                <div class="metric-label">💰 Ventas Totales</div>
            </div>
            <div class="metric-card units">
                <div class="metric-value">{{ report.totales_anuales.unidades_totales }}</div>
                <div class="metric-label">📦 Unidades Vendidas</div>
            </div>
            <div class="metric-card transactions">
                <div class="metric-value">{{ report.totales_anuales.transacciones_totales }}</div>
                <div class="metric-label">🧾 Transacciones</div>
            </div>
            <div class="metric-card customers">
                <div class="metric-value">{{ report.totales_anuales.clientes_únicos }}</div>
                <div class="metric-label">👥 Clientes Únicos</div>
            </div>
            <div class="metric-card products">
                <div class="metric-value">{{ report.totales_anuales.productos_únicos }}</div>
                <div class="metric-label">🏷️ Productos Diferentes</div>
            </div>
        </div>
        
        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label>Vista:</label>
                <select id="viewFilter" onchange="changeView()">
                    <option value="monthly">📅 Por Mes</option>
                    <option value="products">🏷️ Por Productos</option>
                    <option value="customers">👥 Por Clientes</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Métrica:</label>
                <select id="metricFilter" onchange="updateChart()">
                    <option value="ventas">💰 Ventas ($)</option>
                    <option value="unidades">📦 Unidades</option>
                    <option value="transacciones">🧾 Transacciones</option>
                </select>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="content-grid">
            <!-- Monthly Breakdown -->
            <div class="section" id="monthlySection">
                <h3>📅 Desglose Mensual</h3>
                <div class="chart-container">
                    <canvas id="monthlyChart"></canvas>
                </div>
                <div class="monthly-grid">
                    {% for mes, data in report.resumen_mensual.items() %}
                    <div class="month-card">
                        <div class="month-name">{{ ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][mes|int - 1] }}</div>
                        <div class="month-value">${{ "%.0f"|format(data.ventas) }}</div>
                        <div class="month-units">{{ data.unidades }} unidades</div>
                        <div class="month-units">{{ data.transacciones }} transacciones</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Best Analysis -->
            <div class="section">
                <h3>🏆 Mejores del Año</h3>
                
                <h4 style="margin: 20px 0 10px; color: #28a745;">🌟 Mejor Mes en Ventas</h4>
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong>{{ ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][report.análisis.mejor_mes_ventas.mes|int - 1] }}</strong><br>
                    💰 ${{ "%.2f"|format(report.análisis.mejor_mes_ventas.ventas) }}<br>
                    📦 {{ report.análisis.mejor_mes_ventas.unidades }} unidades
                </div>
                
                <h4 style="margin: 20px 0 10px; color: #17a2b8;">📦 Mejor Mes en Unidades</h4>
                <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong>{{ ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][report.análisis.mejor_mes_unidades.mes|int - 1] }}</strong><br>
                    📦 {{ report.análisis.mejor_mes_unidades.unidades }} unidades<br>
                    💰 ${{ "%.2f"|format(report.análisis.mejor_mes_unidades.ventas) }}
                </div>
                
                <h4 style="margin: 20px 0 10px; color: #6c757d;">📊 Promedios</h4>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    💰 Ventas: ${{ "%.2f"|format(report.análisis.promedios.ventas_mensuales) }}/mes<br>
                    📦 Unidades: {{ "%.0f"|format(report.análisis.promedios.unidades_mensuales) }}/mes<br>
                    🧾 Transacciones: {{ "%.0f"|format(report.análisis.promedios.transacciones_mensuales) }}/mes
                </div>
            </div>
        </div>
        
        <!-- Products and Customers -->
        <div class="content-grid">
            <!-- Top Products -->
            <div class="section" id="productsSection">
                <h3>🏷️ Mejores Productos</h3>
                
                <h4 style="margin: 15px 0; color: #28a745;">💰 Por Ventas</h4>
                <ul class="top-list">
                    {% for producto in report.mejores_productos.por_ventas[:5] %}
                    <li>
                        <span class="item-name">{{ producto.nombre }}</span>
                        <div class="item-stats">
                            <div class="item-value">${{ "%.2f"|format(producto.ventas_totales) }}</div>
                            <div class="item-units">{{ producto.unidades_vendidas }} unidades</div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                
                <h4 style="margin: 15px 0; color: #17a2b8;">📦 Por Unidades</h4>
                <ul class="top-list">
                    {% for producto in report.mejores_productos.por_unidades[:5] %}
                    <li>
                        <span class="item-name">{{ producto.nombre }}</span>
                        <div class="item-stats">
                            <div class="item-value">{{ producto.unidades_vendidas }} unidades</div>
                            <div class="item-units">${{ "%.2f"|format(producto.ventas_totales) }}</div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            <!-- Top Customers -->
            <div class="section" id="customersSection">
                <h3>👥 Mejores Clientes</h3>
                
                <h4 style="margin: 15px 0; color: #28a745;">💰 Por Ventas</h4>
                <ul class="top-list">
                    {% for cliente in report.mejores_clientes.por_ventas[:5] %}
                    <li>
                        <span class="item-name">{{ cliente.nombre }}</span>
                        <div class="item-stats">
                            <div class="item-value">${{ "%.2f"|format(cliente.ventas_totales) }}</div>
                            <div class="item-units">{{ cliente.unidades_totales }} unidades</div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                
                <h4 style="margin: 15px 0; color: #17a2b8;">📦 Por Unidades</h4>
                <ul class="top-list">
                    {% for cliente in report.mejores_clientes.por_unidades[:5] %}
                    <li>
                        <span class="item-name">{{ cliente.nombre }}</span>
                        <div class="item-stats">
                            <div class="item-value">{{ cliente.unidades_totales }} unidades</div>
                            <div class="item-units">${{ "%.2f"|format(cliente.ventas_totales) }}</div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <a href="/">🏠 Inicio</a>
            <a href="/sales">📊 Ventas Mensuales</a>
            <a href="/annual_sales">📈 Reporte Anual Simple</a>
            <a href="/disconnect">🚪 Cerrar Sesión</a>
            <br><br>
            <p>&copy; 2025 KH LLOREDA, S.A. | <a href="/terms">Términos</a> | <a href="/privacy">Privacidad</a></p>
        </div>
    </div>
    
    <script>
        let monthlyChart;
        const monthNames = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
        
        // Datos del informe
        const reportData = {{ report|safe }};
        
        function initCharts() {
            const ctx = document.getElementById('monthlyChart').getContext('2d');
            
            const monthlyData = reportData.resumen_mensual;
            const labels = Object.keys(monthlyData).map(m => monthNames[parseInt(m) - 1]);
            const salesData = Object.values(monthlyData).map(d => d.ventas);
            const unitsData = Object.values(monthlyData).map(d => d.unidades);
            const transactionsData = Object.values(monthlyData).map(d => d.transacciones);
            
            monthlyChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Ventas ($)',
                        data: salesData,
                        backgroundColor: 'rgba(40, 167, 69, 0.8)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Ventas ($)'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Evolución Mensual {{ year }}'
                        },
                        legend: {
                            display: true
                        }
                    }
                }
            });
        }
        
        function updateChart() {
            const metric = document.getElementById('metricFilter').value;
            const monthlyData = reportData.resumen_mensual;
            
            let data, label, color;
            switch(metric) {
                case 'ventas':
                    data = Object.values(monthlyData).map(d => d.ventas);
                    label = 'Ventas ($)';
                    color = 'rgba(40, 167, 69, 0.8)';
                    break;
                case 'unidades':
                    data = Object.values(monthlyData).map(d => d.unidades);
                    label = 'Unidades';
                    color = 'rgba(23, 162, 184, 0.8)';
                    break;
                case 'transacciones':
                    data = Object.values(monthlyData).map(d => d.transacciones);
                    label = 'Transacciones';
                    color = 'rgba(255, 193, 7, 0.8)';
                    break;
            }
            
            monthlyChart.data.datasets[0] = {
                label: label,
                data: data,
                backgroundColor: color,
                borderColor: color.replace('0.8', '1'),
                borderWidth: 1
            };
            
            monthlyChart.options.scales.y.title.text = label;
            monthlyChart.update();
        }
        
        function changeView() {
            const view = document.getElementById('viewFilter').value;
            
            // Aquí podrías implementar diferentes vistas
            // Por ahora solo mostramos/ocultamos secciones
            document.getElementById('monthlySection').style.display = view === 'monthly' ? 'block' : 'none';
            document.getElementById('productsSection').style.display = view === 'products' ? 'block' : 'none';
            document.getElementById('customersSection').style.display = view === 'customers' ? 'block' : 'none';
        }
        
        // Inicializar cuando se carga la página
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
        });
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
    auth_url, state_token = qb_client.get_auth_url()
    # Guardar state token en sesión para validación posterior
    session['oauth_state'] = state_token
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
    
    # Validar CSRF protection
    expected_state = session.get('oauth_state')
    if not expected_state or state != expected_state:
        session.pop('oauth_state', None)  # Limpiar state usado
        return render_template_string(
            MAIN_TEMPLATE,
            error="Error de seguridad: Estado OAuth inválido. Por favor, intenta de nuevo."
        )
    
    # Limpiar state token usado
    session.pop('oauth_state', None)
    
    # Intercambiar código por tokens con validación CSRF adicional
    success = qb_client.exchange_code_for_tokens(code, realm_id, expected_state)
    
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

@app.route('/detailed_annual_report')
def detailed_annual_report():
    """Mostrar informe anual detallado con unidades, productos y clientes"""
    try:
        if 'access_token' not in session:
            return redirect('/')
        
        year = request.args.get('year', datetime.now().year, type=int)
        company_id = session['company_id']
        
        # Crear cliente QuickBooks
        qb_client.access_token = session['access_token']
        qb_client.refresh_token = session['refresh_token']
        qb_client.company_id = company_id
        
        # Obtener informe detallado
        detailed_report = qb_client.get_detailed_annual_report(year)
        
        return render_template_string(detailed_annual_template, 
                                    authenticated=True,
                                    company_id=company_id,
                                    report=detailed_report, 
                                    year=year,
                                    current_year=datetime.now().year,
                                    view_type='detailed_annual')
    
    except Exception as e:
        print(f"Error en /detailed_annual_report: {e}")
        return render_template_string(
            MAIN_TEMPLATE,
            authenticated=True,
            company_id=session.get('company_id'),
            view_type='detailed_annual',
            error=f"Error obteniendo informe detallado: {str(e)}"
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

# ============================================================================
# ENDPOINTS API JSON (para OpenWebUI/OpenAPI)
# ============================================================================

@app.route('/api/public/sales')
def api_public_sales_current():
    """API endpoint público para ventas del mes actual (solo cache, sin auth)"""
    try:
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Buscar datos en cache
        session = cache_service.Session()
        period = f"{current_month:02d}/{current_year}"
        
        cached_data = session.query(SalesCache).filter(
            SalesCache.period == period
        ).first()
        
        if cached_data:
            return jsonify({
                'period': cached_data.period,
                'total_sales': float(cached_data.total_sales),
                'receipts_count': cached_data.receipts_count,
                'receipts_total': float(cached_data.receipts_total),
                'invoices_count': cached_data.invoices_count,
                'invoices_total': float(cached_data.invoices_total),
                'fecha_inicio': cached_data.fecha_inicio,
                'fecha_fin': cached_data.fecha_fin,
                'last_updated': cached_data.last_updated.isoformat() if cached_data.last_updated else None,
                'source': 'cache'
            })
        else:
            return jsonify({
                'error': f'No hay datos en cache para {period}',
                'period': period,
                'source': 'cache'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

@app.route('/api/public/sales/<int:year>/<int:month>')
def api_public_sales_specific(year, month):
    """API endpoint público para ventas de un mes específico (solo cache, sin auth)"""
    try:
        if month < 1 or month > 12:
            return jsonify({'error': 'Mes inválido (1-12)'}), 400
        if year < 2020 or year > 2030:
            return jsonify({'error': 'Año inválido (2020-2030)'}), 400
            
        # Buscar datos en cache
        session = cache_service.Session()
        period = f"{month:02d}/{year}"
        
        cached_data = session.query(SalesCache).filter(
            SalesCache.period == period
        ).first()
        
        if cached_data:
            return jsonify({
                'period': cached_data.period,
                'total_sales': float(cached_data.total_sales),
                'receipts_count': cached_data.receipts_count,
                'receipts_total': float(cached_data.receipts_total),
                'invoices_count': cached_data.invoices_count,
                'invoices_total': float(cached_data.invoices_total),
                'fecha_inicio': cached_data.fecha_inicio,
                'fecha_fin': cached_data.fecha_fin,
                'last_updated': cached_data.last_updated.isoformat() if cached_data.last_updated else None,
                'source': 'cache'
            })
        else:
            return jsonify({
                'error': f'No hay datos en cache para {period}',
                'period': period,
                'source': 'cache'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

@app.route('/api/public/annual')
def api_public_annual_current():
    """API endpoint público para reporte anual del año actual (solo cache, sin auth)"""
    try:
        current_year = datetime.now().year
        return api_public_annual_specific(current_year)
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

@app.route('/api/public/annual/<int:year>')
def api_public_annual_specific(year):
    """API endpoint público para reporte anual de un año específico (solo cache, sin auth)"""
    try:
        if year < 2020 or year > 2030:
            return jsonify({'error': 'Año inválido (2020-2030)'}), 400
            
        # Obtener datos anuales del cache
        annual_data = cache_service.get_annual_cached_data(year)
        
        if annual_data and annual_data.get('meses_con_datos', 0) > 0:
            return jsonify(annual_data)
        else:
            return jsonify({
                'error': f'No hay datos anuales en cache para {year}',
                'year': year,
                'source': 'cache'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

@app.route('/api/public/status')
def api_public_status():
    """API endpoint público para estado del sistema (solo cache, sin auth)"""
    try:
        # Obtener estadísticas del cache
        session = cache_service.Session()
        total_records = session.query(SalesCache).count()
        
        if total_records > 0:
            latest_update = session.query(SalesCache.last_updated).order_by(SalesCache.last_updated.desc()).first()
            oldest_record = session.query(SalesCache.period).order_by(SalesCache.period).first()
            newest_record = session.query(SalesCache.period).order_by(SalesCache.period.desc()).first()
            
            return jsonify({
                'sistema': 'QuickBooks Sales Reporter',
                'estado': 'activo',
                'cache': {
                    'total_registros': total_records,
                    'periodo_mas_antiguo': oldest_record[0] if oldest_record else None,
                    'periodo_mas_reciente': newest_record[0] if newest_record else None,
                    'ultima_actualizacion': latest_update[0].isoformat() if latest_update and latest_update[0] else None
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'sistema': 'QuickBooks Sales Reporter',
                'estado': 'activo',
                'cache': {
                    'total_registros': 0,
                    'mensaje': 'No hay datos en cache'
                },
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

# ============================================================================
# API ENDPOINTS PARA INTEGRACIÓN CON OPENWEBUI (SQL QUERIES)
# ============================================================================

@app.route('/api/query/sql', methods=['POST'])
def api_query_sql():
    """API endpoint para ejecutar consultas SQL en el cache de ventas"""
    import re
    import sqlite3
    
    try:
        # Obtener la consulta SQL del request
        data = request.get_json()
        if not data or 'sql' not in data:
            return jsonify({'error': 'Se requiere el campo "sql" en el JSON'}), 400
            
        sql_query = data['sql'].strip()
        
        # Validaciones de seguridad
        forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        sql_upper = sql_query.upper()
        
        for keyword in forbidden_keywords:
            if keyword in sql_upper:
                return jsonify({'error': f'Operación no permitida: {keyword}'}), 403
                
        # Solo permitir SELECT
        if not sql_upper.strip().startswith('SELECT'):
            return jsonify({'error': 'Solo se permiten consultas SELECT'}), 403
            
        # Verificar que solo accede a tablas permitidas
        if 'FROM' in sql_upper:
            # Extraer tablas mencionadas (simplificado)
            tables_pattern = r'FROM\s+(\w+)'
            tables = re.findall(tables_pattern, sql_upper)
            allowed_tables = ['SALES_CACHE', 'PRODUCT_SALES', 'CUSTOMER_SALES']
            for table in tables:
                if table not in allowed_tables:
                    return jsonify({'error': f'Tabla no permitida: {table}. Solo se permiten: {", ".join(allowed_tables)}'}), 403
        
        # Conectar a la base de datos SQLite
        db_path = cache_service.db_path
        
        if not os.path.exists(db_path):
            return jsonify({'error': 'Base de datos no encontrada'}), 404
            
        # Ejecutar la consulta
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        cursor = conn.cursor()
        
        # Agregar LIMIT si no existe (máximo 1000 filas)
        if 'LIMIT' not in sql_upper:
            sql_query += ' LIMIT 1000'
            
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        data_list = []
        for row in results:
            data_list.append(dict(row))
            
        conn.close()
        
        return jsonify({
            'success': True,
            'query': sql_query,
            'row_count': len(data_list),
            'data': data_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except sqlite3.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

@app.route('/api/schema')
def api_schema():
    """API endpoint para obtener el esquema de la base de datos"""
    try:
        return jsonify({
            "database_type": "SQLite",
            "connection_info": "Cache local de datos QuickBooks Online",
            "tables": {
                "sales_cache": {
                    "description": "Cache de resúmenes mensuales de ventas de QuickBooks",
                    "row_count_approx": 50,
                    "columns": {
                        "id": {
                            "type": "INTEGER",
                            "primary_key": True,
                            "description": "ID único de registro"
                        },
                        "company_id": {
                            "type": "TEXT",
                            "description": "ID de empresa QuickBooks (dato sensible, no mostrar)",
                            "example": "9341455133679605"
                        },
                        "period": {
                            "type": "TEXT",
                            "description": "Período en formato MM/YYYY",
                            "examples": ["08/2025", "07/2025", "12/2024"],
                            "pattern": "^\\d{2}/\\d{4}$"
                        },
                        "total_sales": {
                            "type": "FLOAT",
                            "description": "Total de ventas del período en USD",
                            "examples": [4657.82, 1234.50, 0.0]
                        },
                        "receipts_count": {
                            "type": "INTEGER", 
                            "description": "Número de recibos de venta emitidos",
                            "examples": [15, 8, 0]
                        },
                        "receipts_total": {
                            "type": "FLOAT",
                            "description": "Total monetario de recibos de venta",
                            "examples": [2500.30, 800.0, 0.0]
                        },
                        "invoices_count": {
                            "type": "INTEGER",
                            "description": "Número de facturas emitidas", 
                            "examples": [8, 5, 0]
                        },
                        "invoices_total": {
                            "type": "FLOAT",
                            "description": "Total monetario de facturas",
                            "examples": [2157.52, 434.50, 0.0]
                        },
                        "fecha_inicio": {
                            "type": "TEXT",
                            "description": "Fecha inicio del período (YYYY-MM-DD)",
                            "examples": ["2025-08-01", "2025-07-01"]
                        },
                        "fecha_fin": {
                            "type": "TEXT", 
                            "description": "Fecha fin del período (YYYY-MM-DD)",
                            "examples": ["2025-08-31", "2025-07-31"]
                        },
                        "last_updated": {
                            "type": "DATETIME",
                            "description": "Última actualización del registro",
                            "examples": ["2025-08-07T10:48:14.670527"]
                        },
                        "total_units": {
                            "type": "INTEGER",
                            "description": "Total de unidades vendidas en el período",
                            "examples": [150, 85, 0]
                        },
                        "unique_customers": {
                            "type": "INTEGER", 
                            "description": "Número de clientes únicos que compraron en el período",
                            "examples": [12, 8, 0]
                        },
                        "unique_products": {
                            "type": "INTEGER",
                            "description": "Número de productos únicos vendidos en el período",
                            "examples": [5, 3, 0]
                        }
                    },
                    "indexes": [
                        {"columns": ["period"], "description": "Índice por período"},
                        {"columns": ["company_id", "period"], "description": "Índice único empresa-período"}
                    ],
                    "sample_queries": {
                        "ventas_totales_año": {
                            "description": "Total de ventas de un año específico",
                            "sql": "SELECT SUM(total_sales) as total_anual FROM sales_cache WHERE period LIKE '%/2025'",
                            "expected_result": "Una fila con total_anual"
                        },
                        "mejor_mes": {
                            "description": "Mes con mayores ventas",
                            "sql": "SELECT period, total_sales FROM sales_cache ORDER BY total_sales DESC LIMIT 1",
                            "expected_result": "Período y ventas del mejor mes"
                        },
                        "evolución_mensual": {
                            "description": "Ventas mes a mes con crecimiento",
                            "sql": "SELECT period, total_sales, LAG(total_sales) OVER (ORDER BY period) as mes_anterior FROM sales_cache WHERE period LIKE '%/2025' ORDER BY period",
                            "expected_result": "Secuencia temporal con comparación mes anterior"
                        },
                        "resumen_trimestral": {
                            "description": "Ventas agrupadas por trimestre",
                            "sql": "SELECT CASE WHEN SUBSTR(period,1,2) IN ('01','02','03') THEN 'Q1' WHEN SUBSTR(period,1,2) IN ('04','05','06') THEN 'Q2' WHEN SUBSTR(period,1,2) IN ('07','08','09') THEN 'Q3' ELSE 'Q4' END as trimestre, SUM(total_sales) as ventas FROM sales_cache WHERE period LIKE '%/2025' GROUP BY trimestre ORDER BY trimestre",
                            "expected_result": "4 filas con ventas por trimestre"
                        },
                        "estadísticas_transacciones": {
                            "description": "Promedio de transacciones y ventas por mes",
                            "sql": "SELECT AVG(total_sales) as promedio_ventas, AVG(receipts_count + invoices_count) as promedio_transacciones FROM sales_cache WHERE period LIKE '%/2025'",
                            "expected_result": "Promedios calculados"
                        }
                    }
                },
                "product_sales": {
                    "description": "Ventas detalladas por producto y período",
                    "row_count_approx": 200,
                    "columns": {
                        "id": {
                            "type": "INTEGER",
                            "primary_key": True,
                            "description": "ID único de registro"
                        },
                        "company_id": {
                            "type": "TEXT",
                            "description": "ID de empresa QuickBooks (dato sensible)"
                        },
                        "period": {
                            "type": "TEXT",
                            "description": "Período en formato MM/YYYY",
                            "examples": ["08/2025", "07/2025"],
                            "pattern": "^\\d{2}/\\d{4}$"
                        },
                        "product_id": {
                            "type": "TEXT",
                            "description": "ID único del producto en QuickBooks",
                            "examples": ["PROD001", "SERV001"]
                        },
                        "product_name": {
                            "type": "TEXT",
                            "description": "Nombre del producto o servicio",
                            "examples": ["Laptop HP", "Consultoría IT", "Licencia Software"]
                        },
                        "units_sold": {
                            "type": "INTEGER",
                            "description": "Cantidad de unidades vendidas del producto",
                            "examples": [25, 5, 120]
                        },
                        "total_sales": {
                            "type": "FLOAT",
                            "description": "Ventas totales del producto en USD",
                            "examples": [1250.50, 800.0, 3400.75]
                        },
                        "average_price": {
                            "type": "FLOAT", 
                            "description": "Precio promedio por unidad",
                            "examples": [50.02, 160.0, 28.34]
                        },
                        "transactions_count": {
                            "type": "INTEGER",
                            "description": "Número de transacciones que incluyen este producto",
                            "examples": [15, 3, 45]
                        },
                        "unique_customers": {
                            "type": "INTEGER",
                            "description": "Clientes únicos que compraron este producto",
                            "examples": [8, 2, 25]
                        },
                        "last_updated": {
                            "type": "DATETIME",
                            "description": "Última actualización del registro"
                        }
                    },
                    "indexes": [
                        {"columns": ["product_id", "period"], "description": "Índice producto-período"},
                        {"columns": ["period"], "description": "Índice por período"}
                    ]
                },
                "customer_sales": {
                    "description": "Ventas detalladas por cliente y período", 
                    "row_count_approx": 150,
                    "columns": {
                        "id": {
                            "type": "INTEGER",
                            "primary_key": True,
                            "description": "ID único de registro"
                        },
                        "company_id": {
                            "type": "TEXT",
                            "description": "ID de empresa QuickBooks (dato sensible)"
                        },
                        "period": {
                            "type": "TEXT",
                            "description": "Período en formato MM/YYYY",
                            "examples": ["08/2025", "07/2025"],
                            "pattern": "^\\d{2}/\\d{4}$"
                        },
                        "customer_id": {
                            "type": "TEXT",
                            "description": "ID único del cliente en QuickBooks",
                            "examples": ["CLI001", "CUST001"]
                        },
                        "customer_name": {
                            "type": "TEXT",
                            "description": "Nombre del cliente",
                            "examples": ["Empresa ABC S.L.", "Juan Pérez", "Corporación XYZ"]
                        },
                        "total_sales": {
                            "type": "FLOAT",
                            "description": "Ventas totales al cliente en USD",
                            "examples": [2500.75, 450.0, 8900.25]
                        },
                        "total_units": {
                            "type": "INTEGER",
                            "description": "Unidades totales compradas por el cliente",
                            "examples": [45, 8, 150]
                        },
                        "transactions_count": {
                            "type": "INTEGER",
                            "description": "Número de transacciones realizadas",
                            "examples": [12, 2, 28]
                        },
                        "unique_products": {
                            "type": "INTEGER",
                            "description": "Productos únicos comprados por el cliente",
                            "examples": [5, 1, 12]
                        },
                        "last_updated": {
                            "type": "DATETIME",
                            "description": "Última actualización del registro"
                        }
                    },
                    "indexes": [
                        {"columns": ["customer_id", "period"], "description": "Índice cliente-período"},
                        {"columns": ["period"], "description": "Índice por período"}
                    ]
                }
            },
            "query_guidelines": {
                "allowed_operations": ["SELECT"],
                "forbidden_keywords": ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"],
                "allowed_tables": ["sales_cache", "product_sales", "customer_sales"],
                "row_limit": 1000,
                "tips": [
                    "Usa LIKE '%/YYYY' para filtrar por año (ej: '%/2025')",
                    "Usa SUBSTR(period,1,2) para extraer el mes del período",
                    "Usa SUBSTR(period,4,4) para extraer el año del período", 
                    "Para trimestres, agrupa meses: Q1(01,02,03), Q2(04,05,06), etc.",
                    "LAG() y LEAD() están disponibles para análisis temporales",
                    "Usa SUM(), AVG(), COUNT() para agregaciones",
                    "ORDER BY period para secuencias cronológicas",
                    "JOIN entre tablas: sales_cache.period = product_sales.period",
                    "Top productos: ORDER BY units_sold DESC LIMIT 10",
                    "Top clientes: ORDER BY total_sales DESC LIMIT 10",
                    "Análisis de rentabilidad: average_price * units_sold"
                ]
            },
            "common_patterns": {
                "filtro_año": "WHERE period LIKE '%/2025'",
                "filtro_rango_meses": "WHERE period BETWEEN '01/2025' AND '06/2025'",
                "extraer_mes": "CAST(SUBSTR(period,1,2) AS INTEGER) as mes",
                "extraer_año": "CAST(SUBSTR(period,4,4) AS INTEGER) as año",
                "crecimiento_mensual": "LAG(total_sales) OVER (ORDER BY period)",
                "ranking_meses": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
            },
            "sample_queries_extended": {
                "top_productos_unidades": {
                    "description": "Top 5 productos por unidades vendidas en 2025",
                    "sql": "SELECT product_name, SUM(units_sold) as total_units, SUM(total_sales) as total_revenue FROM product_sales WHERE period LIKE '%/2025' GROUP BY product_id, product_name ORDER BY total_units DESC LIMIT 5",
                    "expected_result": "5 productos con mayores unidades vendidas"
                },
                "top_clientes_ventas": {
                    "description": "Top 5 clientes por ventas totales en 2025",
                    "sql": "SELECT customer_name, SUM(total_sales) as total_spent, SUM(total_units) as total_units FROM customer_sales WHERE period LIKE '%/2025' GROUP BY customer_id, customer_name ORDER BY total_spent DESC LIMIT 5",
                    "expected_result": "5 clientes con mayores compras"
                },
                "productos_mas_rentables": {
                    "description": "Productos con mayor precio promedio",
                    "sql": "SELECT product_name, AVG(average_price) as precio_promedio, SUM(units_sold) as unidades_vendidas FROM product_sales WHERE period LIKE '%/2025' GROUP BY product_id, product_name HAVING SUM(units_sold) > 10 ORDER BY precio_promedio DESC",
                    "expected_result": "Productos ordenados por rentabilidad"
                },
                "evolucion_producto_mensual": {
                    "description": "Evolución mensual de ventas de un producto específico",
                    "sql": "SELECT period, product_name, units_sold, total_sales, average_price FROM product_sales WHERE product_name LIKE '%Laptop%' AND period LIKE '%/2025' ORDER BY period",
                    "expected_result": "Evolución temporal de un producto"
                },
                "clientes_mas_fieles": {
                    "description": "Clientes que compraron en más meses diferentes",
                    "sql": "SELECT customer_name, COUNT(DISTINCT period) as meses_activos, SUM(total_sales) as ventas_totales FROM customer_sales WHERE period LIKE '%/2025' GROUP BY customer_id, customer_name ORDER BY meses_activos DESC, ventas_totales DESC",
                    "expected_result": "Clientes más constantes"
                },
                "resumen_completo_mensual": {
                    "description": "Resumen completo con ventas, unidades, productos y clientes por mes",
                    "sql": "SELECT s.period, s.total_sales, s.total_units, s.unique_products, s.unique_customers, s.receipts_count + s.invoices_count as total_transactions FROM sales_cache s WHERE s.period LIKE '%/2025' ORDER BY s.period",
                    "expected_result": "Vista consolidada mensual"
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error del sistema: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Iniciando aplicación QuickBooks Online...")
    print("📋 Pasos para configurar:")
    print("1. Crea una aplicación en https://developer.intuit.com/")
    print("2. Copia config.env.example a .env y configura tus credenciales")
    print("3. Instala dependencias: pip install -r requirements.txt")
    print("4. Visita http://localhost:5000 para comenzar")
    print()
    
    # Configuración para producción o desarrollo
    import os
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)