# 🐳 QuickBooks Online - Contenedor Simple

Versión simplificada para usar con tu infraestructura Nginx y SSL existente.

## 📦 **¿Qué Incluye?**

- **`Dockerfile.simple`** - Imagen Docker solo de la aplicación
- **`docker-compose.simple.yml`** - Compose simplificado
- **`deploy-simple.sh`** - Script de despliegue simple
- **`config.nginx.example`** - Configuración para tu Nginx

## 🚀 **Despliegue Rápido**

### **1. Configurar Variables**
```bash
# Crear archivo de configuración
cp config.production.env .env.production

# Editar con tus credenciales reales
nano .env.production
```

### **2. Desplegar Contenedor**
```bash
# Opción A: Con script
chmod +x deploy-simple.sh
./deploy-simple.sh

# Opción B: Manual
docker build -f Dockerfile.simple -t quickbooks-app .
docker run -d --name quickbooks-app -p 8000:8000 --env-file .env.production quickbooks-app
```

### **3. Configurar tu Nginx**
Agrega a tu configuración de Nginx:

```nginx
location /quickbooks/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### **4. Actualizar QuickBooks Developer**
- Redirect URI: `https://tu-dominio.com/quickbooks/callback`
- (O la URL que configures en tu Nginx)

## 🔧 **Comandos Útiles**

```bash
# Ver logs
docker logs -f quickbooks-app

# Reiniciar
docker restart quickbooks-app

# Actualizar
docker stop quickbooks-app
docker rm quickbooks-app
./deploy-simple.sh

# Estado
docker ps | grep quickbooks
```

## 📍 **Configuración en .env.production**

```env
# Asegúrate de que coincida con tu configuración de Nginx
QB_REDIRECT_URI=https://tu-dominio.com/quickbooks/callback
QB_CLIENT_ID=tu_client_id_real
QB_CLIENT_SECRET=tu_client_secret_real
```

## ✅ **Resultado**

- 🐳 Contenedor corriendo en puerto 8000
- 🔗 Tu Nginx hace proxy a `localhost:8000`
- 🔒 Tu SSL existente maneja HTTPS
- 📊 Acceso a datos reales de QuickBooks

¡Mucho más simple y usa tu infraestructura existente! 🎯