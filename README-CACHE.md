# 🔄 Sistema de Cache Automático - QuickBooks Online

El sistema de cache automático mantiene los datos de ventas actualizados sin intervención manual, mejorando significativamente la experiencia del usuario.

## 🚀 **Características Implementadas**

### **📊 Cache Inteligente con SQLite**
- ✅ **Base de datos local** con SQLite
- ✅ **Resúmenes en tabla principal** para consultas rápidas
- ✅ **Detalles completos en JSON** para información extendida
- ✅ **Timestamps de actualización** para control de freshness
- ✅ **Manejo de errores** con fallback a cache previo

### **⏰ Scheduler Automático**
- ✅ **APScheduler** ejecutándose en background
- ✅ **Actualizaciones cada hora** (configurable)
- ✅ **Registro automático** al autorizar QuickBooks
- ✅ **Limpieza automática** de cache antiguo
- ✅ **Renovación de tokens** OAuth automática

### **🛠️ Endpoints Administrativos**
- ✅ **`/admin/cache/stats`** - Estadísticas del cache
- ✅ **`/admin/scheduler/status`** - Estado del scheduler
- ✅ **`/admin/force-update`** - Actualización manual inmediata
- ✅ **`/admin/cache/history`** - Historial de períodos

## 📁 **Estructura de Archivos**

```
Quickbooks/
├── data/                           # 📂 Datos persistentes
│   ├── sales_cache.db             # 🗄️ Base SQLite principal
│   ├── sales_details_123_2024_08.json # 📄 Detalles JSON por empresa/mes
│   └── sales_details_123_2024_07.json
├── sales_cache.py                 # 🧠 Servicio de cache
├── scheduler.py                   # ⏰ Scheduler automático
├── app.py                         # 🌐 Aplicación principal (actualizada)
└── requirements.txt               # 📦 Dependencias (SQLAlchemy + APScheduler)
```

## 🔧 **Configuración**

### **Variables de Entorno**
```bash
SALES_UPDATE_INTERVAL=1  # Horas entre actualizaciones (default: 1)
```

### **Docker Compose**
```yaml
volumes:
  - ./data:/app/data      # Persistir SQLite y JSON
  - ./logs:/app/logs      # Persistir logs del scheduler
```

## 🎯 **Flujo de Funcionamiento**

### **1. Autorización Inicial**
```
Usuario autoriza → Tokens guardados → Empresa registrada en scheduler → Actualización inmediata
```

### **2. Actualizaciones Automáticas**
```
Cada hora → Scheduler ejecuta → Obtiene datos de QB → Actualiza cache SQLite + JSON
```

### **3. Consulta de Datos**
```
Usuario solicita ventas → Verifica cache → Si existe y es válido: usar cache → Si no: consultar QB + actualizar cache
```

### **4. Manejo de Errores**
```
Error en QB → Mostrar último cache disponible → Continuar intentos automáticos
```

## 📊 **Base de Datos SQLite**

### **Tabla: `sales_cache`**
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
    update_success TEXT DEFAULT 'true', -- 'true'/'false'/'error'
    error_message TEXT                  -- Mensaje de error si aplica
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

## 🎮 **Interfaz de Usuario**

### **Indicadores en la UI**
- 📊 **"Datos desde cache"** - Muestra cuándo se actualizó por última vez
- 🔄 **"Datos en tiempo real"** - Indica consulta directa a QuickBooks
- ⚠️ **"Cache disponible"** - Fallback cuando QuickBooks no es accesible

### **Controles Administrativos**
- **🔄 Forzar Actualización** - Actualización manual inmediata
- **📊 Ver Estadísticas** - Estado del sistema y cache

## 🔍 **Monitoreo y Logs**

### **Logs del Scheduler**
```
🔄 Iniciando actualización programada de ventas: 2024-08-06 14:00:00
✅ Actualizado 123456789: $15234.50
📊 Actualización completada: ✅1 exitosas, ❌0 fallidas
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

## 🚀 **Beneficios del Sistema**

### **👤 Para el Usuario**
- ⚡ **Carga instantánea** - Datos desde cache local
- 🔄 **Siempre actualizado** - Actualizaciones automáticas cada hora
- 🛡️ **Resistente a fallos** - Funciona aunque QuickBooks esté inaccesible
- 📱 **Mejor UX** - No esperas para ver datos

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

## 🔧 **Comandos Útiles**

### **Forzar Actualización Manual**
```bash
curl -X POST http://localhost:8000/admin/force-update
```

### **Ver Estadísticas**
```bash
curl http://localhost:8000/admin/cache/stats
curl http://localhost:8000/admin/scheduler/status
```

### **Verificar Cache en SQLite**
```bash
sqlite3 data/sales_cache.db "SELECT * FROM sales_cache ORDER BY last_updated DESC;"
```

## 🔄 **Configuración Avanzada**

### **Cambiar Frecuencia de Actualización**
```yaml
# docker-compose.yml
environment:
  - SALES_UPDATE_INTERVAL=2  # Cada 2 horas
```

### **Configurar Limpieza de Cache**
El sistema automáticamente limpia entradas más antiguas que 90 días. Para personalizar, modificar en `scheduler.py`:
```python
deleted_count = self.cache_service.cleanup_old_cache(days_to_keep=120)  # 120 días
```

## 🎯 **Próximas Mejoras Posibles**

- 📧 **Notificaciones por email** de resúmenes diarios
- 📊 **Dashboard con gráficas** de tendencias
- 🔔 **Alertas de metas** alcanzadas
- 🌐 **API REST completa** para integración externa
- 📱 **Notificaciones push** para móvil

---

¡El sistema de cache automático está completamente funcional y listo para mejorar significativamente la experiencia con QuickBooks Online! 🎉