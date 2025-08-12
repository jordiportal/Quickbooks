# 📋 Changelog - QuickBooks Sales Reporter

## [v2.0.1] - 2025-08-12

### 🔧 Fixes
- **CRÍTICO**: Corregido error `Could not import module "openapi_server_minimal"` en FastAPI
- **Docker**: Mejorados permisos de directorio data/ para SQLite
- **Flask**: Configurado para usar host `0.0.0.0` en lugar de `127.0.0.1`
- **Production**: Deshabilitado modo DEBUG en producción

### 🏗️ Cambios Técnicos
- Actualizado `uvicorn.run()` para usar `"openapi_server:app"` correctamente
- Flask ahora respeta la variable `FLASK_ENV` para modo debug
- Mejorada configuración de red en contenedores Docker

### 📦 Imagen Docker
- **Registry**: `registry.khlloreda.es/quickbooks-reporter:v2.0.1`
- **Latest**: `registry.khlloreda.es/quickbooks-reporter:latest`
- **Status**: ✅ Funcionando correctamente

---

## [v2.0.0] - 2025-08-12

### ✨ Nuevas Características
- **OpenWebUI Integration**: Servidor FastAPI con 4 endpoints esenciales
- **Esquema Extendido**: Nuevas tablas `product_sales` y `customer_sales`
- **Campos Adicionales**: `total_units`, `unique_customers`, `unique_products`
- **SQL Queries**: Soporte para consultas SQL naturales

### 🗃️ Base de Datos
- Nueva tabla `product_sales` con detalles por producto
- Nueva tabla `customer_sales` con detalles por cliente
- Campos extendidos en `sales_cache`
- Migración automática de esquema

### 🌐 API
- **4 Endpoints únicamente**:
  - `GET /api/schema` - Esquema de base de datos
  - `POST /api/query/sql` - Ejecutar consultas SQL
  - `GET /api/status` - Estado y tamaño de BBDD
  - `POST /admin/force-update` - Forzar actualización

### 🚀 Despliegue
- Soporte Docker completo
- Dual server: Flask (5000) + FastAPI (8080)
- Configuración de producción
- Registry privado en `registry.khlloreda.es`

### 🧹 Limpieza
- Eliminados 18+ archivos innecesarios
- Simplificada estructura del proyecto
- Documentación consolidada

---

## Instrucciones de Actualización

### Desarrollo Local
```bash
# Parar servidores anteriores
docker-compose down

# Obtener nueva imagen
docker pull registry.khlloreda.es/quickbooks-reporter:v2.0.1

# Iniciar con nueva versión
docker-compose -f docker-compose.production.yml up -d
```

### Verificación
```bash
# Verificar Flask
curl http://localhost:5000/

# Verificar FastAPI
curl http://localhost:8080/api/schema

# Verificar estado
curl http://localhost:8080/api/status
```

---

## URLs para OpenWebUI

- **Servidor**: `http://localhost:8080`
- **Documentación**: `http://localhost:8080/docs`
- **Esquema**: `http://localhost:8080/api/schema`

---

**🏢 Desarrollado por KH LLOREDA, S.A.**
