# 🚀 QuickBooks Sales Reporter para OpenWebUI

## 📋 Configuración Final

### 🎯 Endpoints Disponibles (Solo 4)

1. **📊 GET `/api/schema`** - Esquema de base de datos
2. **🧠 POST `/api/query/sql`** - Ejecutar consultas SQL
3. **📈 GET `/api/status`** - Estado y tamaño de BBDD  
4. **🔄 POST `/admin/force-update`** - Forzar actualización

### 🚀 Iniciar Servidores

```bash
# Terminal 1: Flask (Backend)
python app.py

# Terminal 2: FastAPI (OpenWebUI Interface)
python openapi_server.py --host 0.0.0.0 --port 8080
```

### 🔗 Configuración en OpenWebUI

1. **URL**: `http://localhost:8080`
2. **Tipo**: OpenAPI/Swagger
3. **Documentación**: `http://localhost:8080/docs`

### 💡 Datos Disponibles

#### 📊 Tabla `sales_cache` (Principal)
- `period`: Período MM/YYYY
- `total_sales`: Ventas totales USD
- `total_units`: **🆕 Total unidades vendidas**
- `unique_customers`: **🆕 Clientes únicos**
- `unique_products`: **🆕 Productos únicos**
- `receipts_count/total`: Recibos
- `invoices_count/total`: Facturas
- `fecha_inicio/fin`: Fechas del período

#### 📦 Tabla `product_sales` (Nueva)
- `product_name`: Nombre del producto
- `units_sold`: Unidades vendidas
- `total_sales`: Ventas del producto
- `average_price`: Precio promedio
- `unique_customers`: Clientes que lo compraron

#### 👥 Tabla `customer_sales` (Nueva)
- `customer_name`: Nombre del cliente
- `total_sales`: Ventas al cliente
- `total_units`: Unidades compradas
- `unique_products`: Productos únicos comprados

### 🤖 Preguntas de Ejemplo para OpenWebUI

#### 📈 Análisis General
- "¿Cuáles fueron las ventas totales y unidades vendidas este año?"
- "¿Qué mes tuvo más ventas en 2025?"
- "Muestra la evolución mensual de ventas y unidades"

#### 📦 Análisis de Productos
- "¿Cuáles son los 5 productos más vendidos por unidades?"
- "¿Qué productos generan más ingresos?"
- "¿Cuál es el precio promedio de cada producto?"

#### 👥 Análisis de Clientes
- "¿Qué clientes han comprado más este año?"
- "¿Cuáles son los clientes más fieles?"
- "¿Qué cliente tiene mayor diversidad de productos?"

#### 📊 Estado del Sistema
- "¿Cuántos registros hay en la base de datos?"
- "¿Cuál es el estado actual del sistema?"

### 🛠️ Consultas SQL Directas

```sql
-- Resumen mensual completo
SELECT period, total_sales, total_units, unique_customers, unique_products 
FROM sales_cache 
WHERE period LIKE '%/2025' 
ORDER BY period;

-- Top 5 productos por unidades
SELECT product_name, SUM(units_sold) as total_units 
FROM product_sales 
WHERE period LIKE '%/2025' 
GROUP BY product_name 
ORDER BY total_units DESC 
LIMIT 5;

-- Top 5 clientes por ventas
SELECT customer_name, SUM(total_sales) as total_spent 
FROM customer_sales 
WHERE period LIKE '%/2025' 
GROUP BY customer_name 
ORDER BY total_spent DESC 
LIMIT 5;
```

### 🔄 Actualización de Datos

- **Automática**: Cada hora
- **Manual**: Usar endpoint `/admin/force-update`
- **Estado**: Verificar con `/api/status`

### 📁 Archivos Principales

```
quickbooks/
├── app.py                 # Aplicación Flask principal
├── openapi_server.py      # Servidor FastAPI para OpenWebUI
├── quickbooks_client.py   # Cliente QuickBooks API
├── sales_cache.py         # Sistema de cache SQLite
├── scheduler.py           # Actualizaciones automáticas
├── requirements.txt       # Dependencias Python
└── data/
    └── sales_cache.db     # Base de datos SQLite
```

### ✅ Verificación

```bash
# Probar servidor
curl http://localhost:8080/api/status

# Probar consulta SQL
curl -X POST http://localhost:8080/api/query/sql \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT COUNT(*) FROM sales_cache"}'
```

### 🎯 Resultado Final

- ✅ **4 endpoints únicamente** (como solicitado)
- ✅ **Consultas SQL funcionando** con nuevas tablas
- ✅ **Información de unidades, productos y clientes** disponible
- ✅ **Compatible con OpenWebUI** out-of-the-box
- ✅ **Documentación automática** en `/docs`

¡Tu sistema está listo para usar con OpenWebUI! 🚀
