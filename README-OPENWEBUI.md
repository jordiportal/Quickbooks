# 🤖 Integración QuickBooks Sales Reporter + OpenWebUI

**Conecta tu sistema de ventas QuickBooks con OpenWebUI para consultas de chat inteligentes**

Con esta integración puedes hacer preguntas como:
- *"¿Cómo van las ventas de este mes?"*
- *"¿Cuál fue el mejor mes del año?"*
- *"Compara las ventas de 2024 con 2023"*
- *"¿Cuántas facturas se emitieron en julio?"*

## 🚀 **Configuración Rápida**

### **Opción 1: Servidor OpenAPI Independiente**

```bash
# Instalar dependencias
pip install -r requirements-openapi.txt

# Ejecutar servidor Flask principal (en una terminal)
python app.py

# Ejecutar servidor OpenAPI (en otra terminal)
python openapi_server.py --host 0.0.0.0 --port 8080
```

**Configurar en OpenWebUI:**
1. Ve a **Settings** → **Tools** → **OpenAPI**
2. Agrega nueva herramienta:
   - **URL**: `http://localhost:8080`
   - **Name**: `QuickBooks Sales Reporter`
   - **Description**: `Consultar datos de ventas de QuickBooks Online`

### **Opción 2: Docker Compose Completo**

```bash
# Configurar variables de entorno
cp config.env.example .env.production
# Editar .env.production con tus credenciales QuickBooks

# Ejecutar ambos servicios
docker-compose -f docker-compose.openapi.yml up -d
```

**Configurar en OpenWebUI:**
- **URL**: `http://localhost:8080`
- **Name**: `QuickBooks Sales USA`

## 📊 **Endpoints Disponibles**

### **🔍 Consultas de Ventas**
- **`GET /api/sales`** - Ventas del mes actual
- **`GET /api/sales/{year}/{month}`** - Ventas de mes específico
- **`GET /api/annual`** - Reporte anual completo
- **`GET /api/annual/{year}`** - Reporte anual específico

### **📈 Análisis Avanzados**
- **`GET /api/quarterly/{year}`** - Reporte trimestral
- **`GET /api/comparison/{year1}/{year2}`** - Comparación entre años

### **🛠️ Administración**
- **`GET /admin/cache/stats`** - Estadísticas del sistema
- **`POST /admin/force-update`** - Actualización manual
- **`POST /admin/force-annual-update`** - Actualización anual completa

## 🎯 **Ejemplos de Consultas en OpenWebUI**

### **Consultas Básicas**
```
👤 Usuario: "¿Cómo van las ventas de este mes?"
🤖 AI: Consultando las ventas actuales... [GET /api/sales]

👤 Usuario: "¿Cuánto vendimos en julio de 2024?"  
🤖 AI: Obteniendo datos específicos... [GET /api/sales/2024/7]
```

### **Análisis Anuales**
```
👤 Usuario: "Muéstrame el resumen anual de ventas"
🤖 AI: Generando reporte anual... [GET /api/annual]

👤 Usuario: "¿Cuál fue el mejor mes del año?"
🤖 AI: Analizando datos anuales... [GET /api/annual] 
      El mejor mes fue Junio con $15,234.50 en ventas
```

### **Comparaciones**
```
👤 Usuario: "Compara las ventas de 2024 con 2023"
🤖 AI: Realizando comparación... [GET /api/comparison/2024/2023]
      Las ventas crecieron un 27.5% respecto al año anterior
```

### **Consultas Específicas**
```
👤 Usuario: "¿Cuántas facturas se emitieron en el Q2?"
🤖 AI: Consultando datos trimestrales... [GET /api/quarterly/2024]
      En Q2 se emitieron 156 facturas por un total de $45,678.90
```

## 🔧 **Arquitectura del Sistema**

```
┌─────────────────┐    HTTP REST    ┌─────────────────┐    OAuth/Cache    ┌─────────────────┐
│                 │────────────────▶│                 │──────────────────▶│                 │
│   OpenWebUI     │                 │  FastAPI Server │                   │  Flask Server   │
│   (Chat UI)     │◀────────────────│  (API Gateway)  │◀──────────────────│  (QuickBooks)   │
│                 │    JSON Data    │                 │   Sales Data      │                 │
└─────────────────┘                 └─────────────────┘                   └─────────────────┘
                                                                                     │
                                                                                     ▼
                                                                           ┌─────────────────┐
                                                                           │                 │
                                                                           │ QuickBooks API  │
                                                                           │   + SQLite      │
                                                                           │     Cache       │
                                                                           └─────────────────┘
```

### **Componentes:**

1. **🎮 OpenWebUI** - Interfaz de chat para el usuario
2. **🌐 FastAPI Server** (`openapi_server.py`) - API Gateway compatible con OpenAPI
3. **⚙️ Flask Server** (`app.py`) - Servidor principal con lógica de negocio
4. **💾 Cache SQLite** - Almacenamiento local con actualizaciones automáticas
5. **📊 QuickBooks API** - Fuente de datos externa

## 📝 **Configuración Avanzada**

### **Variables de Entorno**

```bash
# Servidor Flask Principal (.env.production)
QB_CLIENT_ID=tu_client_id_aqui
QB_CLIENT_SECRET=tu_client_secret_aqui
QB_REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=tu_clave_secreta_aqui
SALES_UPDATE_INTERVAL=1

# Servidor OpenAPI 
FLASK_BASE_URL=http://localhost:5000  # URL del servidor Flask
LOG_LEVEL=info
```

### **Personalización del Servidor OpenAPI**

```bash
# Cambiar puerto y host
python openapi_server.py --host 0.0.0.0 --port 9000

# Conectar a servidor Flask remoto
python openapi_server.py --flask-url http://remote-server:5000

# Modo desarrollo con recarga automática
python openapi_server.py --reload --log-level debug
```

### **Docker Compose Personalizado**

```yaml
# docker-compose.openapi.yml
services:
  quickbooks-openapi:
    ports:
      - "9000:8080"  # Cambiar puerto externo
    environment:
      - FLASK_BASE_URL=http://quickbooks-app:5000
      - LOG_LEVEL=debug
```

## 🔒 **Seguridad y Autenticación**

### **Flujo de Autenticación**
1. **Usuario autoriza** QuickBooks en `http://localhost:5000/auth`
2. **Sesión establecida** en servidor Flask
3. **OpenAPI Server** actúa como proxy autenticado
4. **OpenWebUI** hace consultas sin manejar OAuth directamente

### **Consideraciones de Seguridad**
- 🔐 **OAuth tokens** manejados solo por el servidor Flask
- 🛡️ **CORS configurado** para dominios específicos en producción
- 📊 **Rate limiting** en endpoints para evitar abuso
- 🔍 **Logging detallado** para auditoría

## 🎯 **Casos de Uso Empresariales**

### **Análisis Diario**
```
"¿Cómo van las ventas hoy comparado con ayer?"
"¿Qué facturas están pendientes este mes?"
"Muéstrame el resumen semanal de recibos"
```

### **Planificación Mensual**
```
"¿Vamos a cumplir el objetivo mensual?"
"¿Cuál es la tendencia de ventas este trimestre?"
"Compara este mes con el mismo mes del año pasado"
```

### **Reportes Ejecutivos**
```
"Genera un resumen anual para la junta directiva"
"¿Cuáles fueron los mejores y peores meses?"
"¿Cómo ha evolucionado el negocio este año?"
```

### **Análisis de Tendencias**
```
"¿Hay algún patrón estacional en las ventas?"
"¿En qué trimestre vendemos más?"
"¿Cómo se compara nuestro crecimiento con años anteriores?"
```

## 🛠️ **Troubleshooting**

### **Problemas Comunes**

**❌ Error: "No se puede conectar con el servidor QuickBooks"**
```bash
# Verificar que el servidor Flask esté ejecutándose
curl http://localhost:5000

# Verificar logs del servidor Flask
docker logs quickbooks-app
```

**❌ Error: "No autenticado con QuickBooks"**
```bash
# Ir al servidor Flask y autorizar
open http://localhost:5000/auth

# Verificar estado de autenticación
curl http://localhost:5000/admin/scheduler/status
```

**❌ Error: "Timeout conectando con QuickBooks"**
```bash
# El servidor puede estar procesando datos anuales
# Esperar o verificar logs para ver progreso
docker logs quickbooks-app -f
```

### **Verificación del Sistema**

```bash
# Health check del API server
curl http://localhost:8080/health

# Verificar endpoints disponibles
curl http://localhost:8080/

# Probar endpoint específico
curl http://localhost:8080/api/sales
```

### **Logs y Debugging**

```bash
# Logs del servidor OpenAPI
python openapi_server.py --log-level debug

# Logs del servidor Flask
tail -f logs/app.log

# Logs de Docker
docker-compose -f docker-compose.openapi.yml logs -f
```

## 📚 **Documentación API**

### **Swagger UI**
- **URL**: `http://localhost:8080/docs`
- **Interactiva**: Probar endpoints directamente
- **Esquemas**: Ver estructuras de datos completas

### **OpenAPI Spec**
- **URL**: `http://localhost:8080/openapi.json`
- **YAML**: Ver `openapi_spec.yaml` en el repositorio
- **Compatible**: Estándar OpenAPI 3.0.3

### **Redoc**
- **URL**: `http://localhost:8080/redoc`
- **Documentación**: Formato alternativo más legible

## 🌟 **Características Avanzadas**

### **Cache Inteligente**
- ⚡ **Respuestas rápidas** desde cache SQLite local
- 🔄 **Actualizaciones automáticas** cada hora
- 📊 **Fallback** a datos históricos si QuickBooks no disponible

### **Análisis Automático**
- 📈 **Detección automática** de mejor/peor mes
- 📊 **Cálculo de tendencias** y porcentajes de crecimiento
- 🎯 **Métricas KPI** incluidas en todas las respuestas

### **Escalabilidad**
- 🐳 **Docker ready** para despliegue en producción
- 🔧 **Configuración flexible** via variables de entorno
- 📊 **Monitoreo** con health checks y métricas

---

## 🏢 **Soporte Empresarial**

**Desarrollado por**: KH LLOREDA, S.A.
- **Email**: lopd@khlloreda.com
- **Teléfono**: 938492633
- **GitHub**: https://github.com/jordiportal/Quickbooks

**¡Transforma tu gestión de ventas con IA conversacional!** 🚀🤖📊