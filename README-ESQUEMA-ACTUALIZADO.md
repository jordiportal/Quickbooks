# 📊 Esquema Actualizado para OpenWebUI

## 🎯 Resumen de Cambios

Hemos actualizado completamente el esquema de la base de datos para que OpenWebUI pueda consultar información detallada sobre **unidades**, **productos** y **clientes**.

## 🆕 Nuevas Características

### 📊 Tabla `sales_cache` (Actualizada)
Se agregaron nuevos campos:
- `total_units` (INTEGER): Total de unidades vendidas en el período
- `unique_customers` (INTEGER): Número de clientes únicos que compraron
- `unique_products` (INTEGER): Número de productos únicos vendidos

### 📦 Tabla `product_sales` (Nueva)
Ventas detalladas por producto y período:
- `product_id`: ID único del producto en QuickBooks
- `product_name`: Nombre del producto o servicio
- `units_sold`: Cantidad de unidades vendidas
- `total_sales`: Ventas totales del producto en USD
- `average_price`: Precio promedio por unidad
- `transactions_count`: Número de transacciones
- `unique_customers`: Clientes únicos que compraron este producto

### 👥 Tabla `customer_sales` (Nueva)
Ventas detalladas por cliente y período:
- `customer_id`: ID único del cliente en QuickBooks
- `customer_name`: Nombre del cliente
- `total_sales`: Ventas totales al cliente en USD
- `total_units`: Unidades totales compradas
- `transactions_count`: Número de transacciones realizadas
- `unique_products`: Productos únicos comprados

## 🚀 Configuración para OpenWebUI

### 1. Iniciar Servidores
```bash
# Terminal 1: Iniciar Flask
python app.py

# Terminal 2: Iniciar FastAPI para OpenWebUI
python openapi_server.py --host 0.0.0.0 --port 8080
```

### 2. URLs para Configurar en OpenWebUI
- **Servidor principal**: `http://localhost:8080`
- **Esquema de BD**: `http://localhost:8080/api/schema`
- **Consultas SQL**: `http://localhost:8080/api/query/sql`
- **Documentación**: `http://localhost:8080/docs`

### 3. Configuración en OpenWebUI
1. Ir a **Settings** → **Tools**
2. Agregar nueva herramienta
3. **URL**: `http://localhost:8080`
4. **Tipo**: OpenAPI/Swagger
5. El esquema se cargará automáticamente

## 💡 Ejemplos de Preguntas para OpenWebUI

### 📈 Análisis de Ventas
- "¿Cuáles fueron las ventas totales y unidades vendidas en agosto 2025?"
- "Muestra la evolución de ventas y unidades mes a mes en 2025"
- "¿Qué mes tuvo más unidades vendidas este año?"

### 📦 Análisis de Productos
- "¿Cuáles son los 5 productos más vendidos por unidades?"
- "¿Qué productos generan más ingresos por unidad?"
- "¿Cuál es el precio promedio de cada producto?"
- "Muestra los productos más rentables"

### 👥 Análisis de Clientes
- "¿Qué clientes han comprado más unidades este año?"
- "¿Cuáles son los 5 clientes que más dinero han gastado?"
- "¿Qué clientes son más fieles (compran cada mes)?"
- "¿Qué cliente tiene la mayor diversidad de productos?"

### 🔄 Análisis Comparativos
- "Compara las ventas por trimestre"
- "¿Cómo ha evolucionado el número de clientes únicos por mes?"
- "¿Qué productos han crecido más en ventas?"

## 🔍 Consultas SQL de Ejemplo

### Top 5 Productos por Unidades
```sql
SELECT product_name, SUM(units_sold) as total_units, SUM(total_sales) as total_revenue 
FROM product_sales 
WHERE period LIKE '%/2025' 
GROUP BY product_id, product_name 
ORDER BY total_units DESC 
LIMIT 5
```

### Top 5 Clientes por Ventas
```sql
SELECT customer_name, SUM(total_sales) as total_spent, SUM(total_units) as total_units 
FROM customer_sales 
WHERE period LIKE '%/2025' 
GROUP BY customer_id, customer_name 
ORDER BY total_spent DESC 
LIMIT 5
```

### Resumen Completo Mensual
```sql
SELECT s.period, s.total_sales, s.total_units, s.unique_products, s.unique_customers 
FROM sales_cache s 
WHERE s.period LIKE '%/2025' 
ORDER BY s.period
```

### Productos Más Rentables
```sql
SELECT product_name, AVG(average_price) as precio_promedio, SUM(units_sold) as unidades 
FROM product_sales 
WHERE period LIKE '%/2025' 
GROUP BY product_id, product_name 
HAVING SUM(units_sold) > 5 
ORDER BY precio_promedio DESC
```

## 🔄 Actualización de Datos

### Automática
- Los datos se actualizan automáticamente cada hora
- Los nuevos campos se llenan en la próxima actualización
- El sistema mantiene cache local para respuestas rápidas

### Manual
Para forzar una actualización inmediata:
```bash
curl -X POST http://localhost:5000/admin/force-update
```

## 🧪 Verificar Instalación

```bash
# Probar esquema actualizado
python check_schema.py

# Probar compatibilidad completa
python test_complete_setup.py
```

## 📋 Estructura de Tablas Completa

### sales_cache
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| company_id | TEXT | ID empresa QuickBooks |
| period | TEXT | Período MM/YYYY |
| total_sales | FLOAT | Ventas totales USD |
| **total_units** | **INTEGER** | **🆕 Total unidades vendidas** |
| **unique_customers** | **INTEGER** | **🆕 Clientes únicos** |
| **unique_products** | **INTEGER** | **🆕 Productos únicos** |
| receipts_count | INTEGER | Número de recibos |
| receipts_total | FLOAT | Total recibos USD |
| invoices_count | INTEGER | Número de facturas |
| invoices_total | FLOAT | Total facturas USD |
| fecha_inicio | TEXT | Fecha inicio período |
| fecha_fin | TEXT | Fecha fin período |
| last_updated | DATETIME | Última actualización |

### product_sales (🆕 Nueva)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| company_id | TEXT | ID empresa QuickBooks |
| period | TEXT | Período MM/YYYY |
| product_id | TEXT | ID producto QuickBooks |
| product_name | TEXT | Nombre del producto |
| units_sold | INTEGER | Unidades vendidas |
| total_sales | FLOAT | Ventas totales USD |
| average_price | FLOAT | Precio promedio |
| transactions_count | INTEGER | Número transacciones |
| unique_customers | INTEGER | Clientes únicos |
| last_updated | DATETIME | Última actualización |

### customer_sales (🆕 Nueva)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| company_id | TEXT | ID empresa QuickBooks |
| period | TEXT | Período MM/YYYY |
| customer_id | TEXT | ID cliente QuickBooks |
| customer_name | TEXT | Nombre del cliente |
| total_sales | FLOAT | Ventas totales USD |
| total_units | INTEGER | Unidades totales |
| transactions_count | INTEGER | Número transacciones |
| unique_products | INTEGER | Productos únicos |
| last_updated | DATETIME | Última actualización |

## 🎯 Próximos Pasos

1. **Ejecutar migración** (ya completada): ✅
2. **Iniciar servidores**: `python app.py` y `python openapi_server.py`
3. **Configurar OpenWebUI** con URL: `http://localhost:8080`
4. **Probar consultas** usando los ejemplos proporcionados
5. **Forzar actualización** si es necesario para poblar nuevos campos

## 🛠️ Troubleshooting

### Error 503 en FastAPI
- Verificar que Flask esté corriendo en puerto 5000
- Verificar que no hay conflictos de puertos

### Tablas vacías
- Ejecutar actualización manual: `/admin/force-update`
- Los datos se llenan en la próxima sincronización con QuickBooks

### OpenWebUI no encuentra herramienta
- Verificar URL: `http://localhost:8080`
- Verificar que ambos servidores estén corriendo
- Probar acceso a `/docs` para confirmar documentación
