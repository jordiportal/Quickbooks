# 🚀 Despliegue en Producción - QuickBooks Sales Reporter

## 📋 Imágenes Publicadas

Las imágenes están disponibles en el registry privado de KH LLOREDA:

- **Versión específica**: `registry.khlloreda.es/quickbooks-reporter:v2.0.0`
- **Última versión**: `registry.khlloreda.es/quickbooks-reporter:latest`

## 🔧 Despliegue Rápido

### 1. Preparar Entorno

```bash
# Crear directorios de datos
mkdir -p data logs

# Configurar archivos de entorno
cp .env.production.example .env.production
# Editar .env.production con credenciales reales
```

### 2. Desplegar con Docker Compose

```bash
# Desplegar en producción
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Verificar estado
docker-compose -f docker-compose.production.yml ps
```

### 3. Verificar Funcionamiento

```bash
# Verificar Flask (aplicación principal)
curl http://localhost:5000/

# Verificar FastAPI (OpenWebUI)
curl http://localhost:8080/api/schema

# Verificar estado del sistema
curl http://localhost:8080/api/status
```

## 🌐 URLs de Producción

### Aplicación Principal
- **Web UI**: `http://your-server:5000`
- **API**: `http://your-server:5000/api/`

### OpenWebUI Interface
- **OpenAPI Docs**: `http://your-server:8080/docs`
- **Schema**: `http://your-server:8080/api/schema`
- **SQL Queries**: `http://your-server:8080/api/query/sql`
- **Status**: `http://your-server:8080/api/status`
- **Force Update**: `http://your-server:8080/admin/force-update`

## 📊 Configuración OpenWebUI

Para conectar OpenWebUI con tu servidor de producción:

1. **URL del servidor**: `http://your-server:8080`
2. **Tipo**: OpenAPI/Swagger
3. **Documentación**: Se carga automáticamente

## 🔄 Gestión de Imágenes

### Actualizar a Nueva Versión

```bash
# Parar servicios
docker-compose -f docker-compose.production.yml down

# Descargar nueva imagen
docker pull registry.khlloreda.es/quickbooks-reporter:latest

# Reiniciar servicios
docker-compose -f docker-compose.production.yml up -d
```

### Limpiar Imágenes Antiguas

```bash
# Ver imágenes locales
docker images | grep quickbooks-reporter

# Eliminar imágenes no utilizadas
docker image prune
```

## 🔒 Configuración de Seguridad

### Variables de Entorno Requeridas (.env.production)

```env
# QuickBooks OAuth
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REDIRECT_URI=https://your-domain.com/auth/callback

# Base URLs
QUICKBOOKS_BASE_URL=https://sandbox-quickbooks.api.intuit.com
QUICKBOOKS_DISCOVERY_DOCUMENT_URL=https://appcenter.intuit.com/api/v1/OpenID_OIDC_Service

# Cache Settings
SALES_UPDATE_INTERVAL=1

# Security
FLASK_SECRET_KEY=your_secure_secret_key
FLASK_ENV=production
```

### Archivos Sensibles

- **`.env.production`**: Configuración de producción (NO incluir en Git)
- **`data/`**: Base de datos SQLite (persistente)
- **`logs/`**: Logs de aplicación (persistente)

## 📈 Monitoreo

### Health Checks

```bash
# Estado del contenedor
docker-compose -f docker-compose.production.yml ps

# Logs en tiempo real
docker-compose -f docker-compose.production.yml logs -f quickbooks-reporter

# Estado de la aplicación
curl http://localhost:8080/api/status
```

### Métricas Disponibles

El endpoint `/api/status` proporciona:
- Número de registros en cache
- Última actualización
- Estado de conexión con QuickBooks
- Estadísticas de uso

## 🚨 Troubleshooting

### Problemas Comunes

1. **Puerto ocupado**:
   ```bash
   # Verificar qué usa el puerto
   netstat -tulpn | grep :8080
   
   # Cambiar puerto en docker-compose.production.yml
   ports:
     - "8081:8080"  # Usar puerto 8081 externo
   ```

2. **Problemas de configuración**:
   ```bash
   # Verificar montaje de archivos
   docker exec quickbooks-reporter-prod ls -la /app/
   
   # Verificar variables de entorno
   docker exec quickbooks-reporter-prod env | grep QUICKBOOKS
   ```

3. **Base de datos corrupta**:
   ```bash
   # Respaldar datos
   cp data/sales_cache.db data/sales_cache.db.backup
   
   # Forzar reconstrucción
   rm data/sales_cache.db
   docker-compose -f docker-compose.production.yml restart
   ```

## 🔄 Backup y Restauración

### Backup Automático

```bash
#!/bin/bash
# backup-quickbooks.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/quickbooks"

mkdir -p $BACKUP_DIR

# Backup base de datos
cp data/sales_cache.db $BACKUP_DIR/sales_cache_$DATE.db

# Backup configuración
cp .env.production $BACKUP_DIR/env_production_$DATE

# Limpiar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

### Restauración

```bash
# Parar servicios
docker-compose -f docker-compose.production.yml down

# Restaurar base de datos
cp /backups/quickbooks/sales_cache_YYYYMMDD_HHMMSS.db data/sales_cache.db

# Reiniciar servicios
docker-compose -f docker-compose.production.yml up -d
```

## 📝 Logs y Debugging

### Ubicación de Logs

- **Contenedor**: `/app/logs/`
- **Host**: `./logs/`
- **Docker logs**: `docker logs quickbooks-reporter-prod`

### Niveles de Log

- **INFO**: Operaciones normales
- **WARNING**: Situaciones de atención
- **ERROR**: Errores que requieren intervención

## 🏢 Desarrollado por KH LLOREDA, S.A.

- **Versión**: v2.0.0
- **Contacto**: soporte@khlloreda.es
- **Registry**: registry.khlloreda.es
