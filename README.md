# 📊 QuickBooks Online Sales Reporter

**Sistema automático de reporte de ventas con cache inteligente para QuickBooks Online**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🚀 **Características Principales**

### **⚡ Cache Automático Inteligente**
- 📊 **Base de datos SQLite** para resúmenes rápidos
- 📄 **Archivos JSON** para detalles completos de transacciones
- 🔄 **Actualizaciones automáticas** cada hora (configurable)
- 🛡️ **Resistente a fallos** - funciona aunque QuickBooks esté inaccesible
- 📈 **Datos históricos** - mantiene períodos anteriores

### **🔄 Scheduler Automático**
- ⏰ **APScheduler** ejecutándose en background
- 🎯 **Registro automático** al autorizar QuickBooks
- 🧹 **Limpieza automática** de cache antiguo (>90 días)
- 🔄 **Renovación automática** de tokens OAuth
- 📊 **Monitoreo** y estadísticas en tiempo real

### **🎮 Interfaz de Usuario**
- 📱 **Responsive design** optimizado para móvil y desktop
- 🔄 **Indicadores de cache** (tiempo real vs datos en cache)
- 🎛️ **Controles administrativos** integrados
- 📊 **Botón "Ver Estadísticas"** del sistema
- 🔄 **Botón "Forzar Actualización"** manual

### **🛠️ Endpoints Administrativos**
- `/admin/cache/stats` - Estadísticas del cache
- `/admin/scheduler/status` - Estado del scheduler
- `/admin/force-update` - Actualización manual inmediata
- `/admin/cache/history` - Historial de períodos
- 🔐 **Todos requieren autenticación** QuickBooks

### **📋 Páginas Legales**
- ⚖️ **Términos y Condiciones** GDPR-compliant
- 🔒 **Política de Privacidad** para uso empresarial
- 🏢 **Datos de empresa** KH LLOREDA, S.A. integrados

## 🏗️ **Arquitectura del Sistema**

```
📁 Quickbooks/
├── 🐍 app.py                     # Aplicación Flask principal
├── 🔗 quickbooks_client.py       # Cliente API QuickBooks
├── 💾 sales_cache.py             # Sistema de cache SQLite
├── ⏰ scheduler.py               # Scheduler automático
├── 📦 requirements.txt           # Dependencias Python
├── 🐳 Dockerfile               # Imagen Docker
├── 🐳 docker-compose.yml       # Orquestación de contenedores
├── 📁 templates/               # Templates HTML
│   ├── 📜 terminos.html         # Términos y condiciones
│   └── 🔒 privacidad.html       # Política de privacidad
├── 📁 data/                    # Datos persistentes (no en Git)
│   ├── 🗄️ sales_cache.db       # Base SQLite
│   └── 📄 sales_details_*.json  # Detalles por empresa/mes
└── 📚 README-*.md              # Documentación específica
```

## 🚀 **Instalación y Configuración**

### **🔧 Opción 1: Desarrollo Local**

1. **Clonar repositorio:**
   ```bash
   git clone https://github.com/jordiportal/Quickbooks.git
   cd Quickbooks
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp config.env.example .env
   # Editar .env con tus credenciales de QuickBooks
   ```

4. **Ejecutar aplicación:**
   ```bash
   python app.py
   ```
   Visita: `http://localhost:5000`

### **🐳 Opción 2: Docker (Recomendado para Producción)**

1. **Configurar variables de producción:**
   ```bash
   cp config.env.example .env.production
   # Editar .env.production con credenciales reales
   ```

2. **Ejecutar con Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   Aplicación disponible en: `http://localhost:8000`

3. **Verificar estado:**
   ```bash
   docker logs quickbooks-app
   ```

## ⚙️ **Configuración de QuickBooks Online**

### **1. Crear Aplicación en QuickBooks Developer**

1. Ve a [QuickBooks Developer](https://developer.intuit.com/)
2. Crea una nueva aplicación
3. Configura las URLs:
   - **Redirect URI**: `http://localhost:5000/callback` (desarrollo)
   - **Redirect URI**: `https://tu-dominio.com/callback` (producción)

### **2. Configurar Variables de Entorno**

```bash
# Credenciales QuickBooks
QB_CLIENT_ID=tu_client_id_aqui
QB_CLIENT_SECRET=tu_client_secret_aqui
QB_REDIRECT_URI=http://localhost:5000/callback
QB_SANDBOX_BASE_URL=https://sandbox-quickbooks.api.intuit.com
QB_DISCOVERY_URL=https://appcenter.intuit.com/connect/oauth2/.well-known/openid_configuration

# Configuración aplicación
SECRET_KEY=tu_clave_secreta_aqui
SALES_UPDATE_INTERVAL=1  # Horas entre actualizaciones
```

## 🎯 **Flujo de Funcionamiento**

### **1. Proceso de Autorización**
```
Usuario → Autorizar QB → Tokens guardados → Empresa registrada → Actualización inmediata
```

### **2. Actualizaciones Automáticas**
```
Cada hora → Scheduler ejecuta → Obtiene datos QB → Actualiza cache SQLite + JSON
```

### **3. Consulta de Datos**
```
Usuario solicita → Verifica cache → Si válido: usar cache → Si no: consultar QB + actualizar
```

### **4. Manejo de Errores**
```
Error QB → Mostrar último cache → Continuar intentos automáticos → Logs detallados
```

## 📊 **Datos y Persistencia**

### **Base de Datos SQLite** (`sales_cache.db`)
```sql
CREATE TABLE sales_cache (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,           -- ID empresa QuickBooks
    period TEXT NOT NULL,               -- MM/YYYY
    total_sales REAL DEFAULT 0.0,       -- Total ventas
    receipts_count INTEGER DEFAULT 0,   -- Cantidad recibos
    receipts_total REAL DEFAULT 0.0,    -- Total recibos
    invoices_count INTEGER DEFAULT 0,   -- Cantidad facturas
    invoices_total REAL DEFAULT 0.0,    -- Total facturas
    fecha_inicio TEXT,                  -- YYYY-MM-DD
    fecha_fin TEXT,                     -- YYYY-MM-DD
    last_updated TIMESTAMP,             -- Última actualización
    update_success TEXT DEFAULT 'true', -- Estado actualización
    error_message TEXT                  -- Mensaje error si aplica
);
```

### **Archivos JSON de Detalles**
```json
{
  "período": "08/2024",
  "total_ventas": 15234.50,
  "detalle_transacciones": {
    "recibos": [...],
    "facturas": [...]
  },
  "cached_at": "2024-08-06T13:30:15",
  "cache_version": "1.0"
}
```

## 🛠️ **API Endpoints**

### **Endpoints Públicos**
- `GET /` - Página principal
- `GET /auth` - Iniciar autorización QuickBooks
- `GET /callback` - Callback OAuth QuickBooks
- `GET /sales` - Ver reporte de ventas
- `GET /terms` - Términos y condiciones
- `GET /privacy` - Política de privacidad
- `GET /disconnect` - Cerrar sesión

### **Endpoints Administrativos** (requieren autenticación)
- `GET /admin/cache/stats` - Estadísticas del cache
- `GET /admin/scheduler/status` - Estado del scheduler
- `POST /admin/force-update` - Forzar actualización
- `GET /admin/cache/history` - Historial de cache

### **API JSON**
- `GET /api/sales` - Datos de ventas en formato JSON

## 📈 **Monitoreo y Estadísticas**

### **Logs del Sistema**
```bash
# Ver logs en desarrollo
tail -f logs/app.log

# Ver logs en Docker
docker logs quickbooks-app -f
```

### **Estadísticas Disponibles**
```json
{
  "total_entries": 5,
  "successful_updates": 4,
  "failed_updates": 1,
  "latest_update": "2024-08-06T14:00:15",
  "scheduler_running": true,
  "active_companies": 1
}
```

## 🔧 **Comandos Útiles**

### **Desarrollo**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python app.py

# Ver estado del cache
sqlite3 data/sales_cache.db "SELECT * FROM sales_cache;"
```

### **Docker**
```bash
# Construir imagen
docker build -t quickbooks-app .

# Ejecutar con compose
docker-compose up -d

# Ver logs
docker logs quickbooks-app

# Entrar al contenedor
docker exec -it quickbooks-app bash

# Reiniciar aplicación
docker-compose restart
```

### **Producción**
```bash
# Despliegue simple
./deploy.sh

# Verificar estado
curl http://localhost:8000

# Forzar actualización
curl -X POST http://localhost:8000/admin/force-update

# Ver estadísticas
curl http://localhost:8000/admin/cache/stats
```

## 🔒 **Seguridad**

- ✅ **Tokens OAuth** almacenados de forma segura
- ✅ **Endpoints administrativos** protegidos por autenticación
- ✅ **Variables de entorno** para credenciales sensibles
- ✅ **Usuario no privilegiado** en Docker
- ✅ **Validación** de inputs y parámetros
- ✅ **Logs** detallados para auditoría

## 🌐 **Producción**

### **Requisitos de Infraestructura**
- **Python 3.11+**
- **Docker & Docker Compose**
- **Nginx** (para proxy reverso)
- **SSL/HTTPS** (certificado válido)
- **Dominio** configurado

### **Configuración Nginx**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📚 **Documentación Adicional**

- [📄 README-CACHE.md](./README-CACHE.md) - Sistema de cache detallado
- [🐳 README-DOCKER.md](./README-DOCKER.md) - Configuración Docker
- [⚖️ LEGAL-SETUP.md](./LEGAL-SETUP.md) - Configuración páginas legales

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🏢 **Empresa**

**KH LLOREDA, S.A.**
- **Dirección**: Passeig de la Ribera, 111 8420 P. I. Can Castells CANOVELLES
- **Teléfono**: 938492633
- **Email**: lopd@khlloreda.com
- **NIF**: A58288598
- **Registro Mercantil**: Barcelona, Tomo 8062, Folio 091, Hoja 92596

---

## 🎯 **Beneficios del Sistema**

### **👤 Para el Usuario**
- ⚡ **Carga instantánea** - Datos desde cache local
- 🔄 **Siempre actualizado** - Actualizaciones automáticas cada hora
- 🛡️ **Resistente a fallos** - Funciona aunque QuickBooks esté inaccesible
- 📱 **Mejor UX** - Interfaz moderna y responsive

### **⚙️ Para el Sistema**
- 📉 **Menos llamadas API** - Reduce carga en QuickBooks
- 🔄 **Renovación automática** de tokens OAuth
- 📊 **Datos históricos** - Mantiene períodos anteriores
- 🧹 **Auto-limpieza** - Elimina datos antiguos automáticamente

### **🏢 Para el Negocio**
- 📈 **Mejor rendimiento** - Sistema más rápido y confiable
- 💰 **Menor costo** - Menos uso de API QuickBooks
- 📊 **Análisis histórico** - Acceso a datos de meses anteriores
- 🔍 **Monitoreo** - Visibilidad del estado del sistema

---

**¡Desarrollado con ❤️ para automatizar y mejorar la gestión de ventas con QuickBooks Online!** 🎉