# 📄 Configuración de Páginas Legales

Para que QuickBooks apruebe tu aplicación en producción, necesitas personalizar las páginas legales creadas.

## 🔧 **Archivos a Personalizar**

### **1. Términos y Condiciones** (`templates/terminos.html`)
### **2. Política de Privacidad** (`templates/privacidad.html`)

## ✅ **Información Empresarial Configurada**

Las páginas legales ya están configuradas con los datos de **KH LLOREDA, S.A.**:

### **📍 Información Empresarial:**
- **Empresa:** KH LLOREDA, S.A.
- **NIF:** A58288598
- **Dirección:** Passeig de la Ribera, 111 8420 P. I. Can Castells CANOVELLES
- **Teléfono:** 938492633
- **Email principal:** lopd@khlloreda.com
- **Email legal:** monicagarcia@khlloreda.com

### **📧 Emails Configurados:**
- **LOPD/Privacidad:** lopd@khlloreda.com
- **Asuntos legales:** monicagarcia@khlloreda.com

### **🏢 Registro Mercantil:**
- **Registro:** Barcelona, Tomo 8062, Folio 091, Hoja 92596, Inscripción 1a

## 🌐 **URLs para QuickBooks Developer**

Una vez desplegado, configura en QuickBooks:

- **End-user License Agreement URL:** `https://tu-dominio.com/terms`
- **Privacy Policy URL:** `https://tu-dominio.com/privacy`

## 🎯 **URLs Configuradas**

Las páginas legales están listas con los datos de KH LLOREDA:

**URLs para QuickBooks Developer:**
```
End-user License Agreement: https://tu-dominio-real.com/terms
Privacy Policy: https://tu-dominio-real.com/privacy
```

**Emails de contacto configurados:**
```
LOPD/Privacidad: lopd@khlloreda.com
Legal: monicagarcia@khlloreda.com
```

## ⚖️ **Consideraciones Legales**

### **Importante:**
- Estas plantillas cumplen con GDPR pero son **genéricas**
- **Consulta con un abogado** para casos específicos
- Adapta según tu modelo de negocio
- Revisa regularmente para cumplir cambios normativos

### **Elementos Clave Incluidos:**
- ✅ Cumplimiento GDPR (UE)
- ✅ Derechos del usuario
- ✅ Base legal del tratamiento
- ✅ Retención de datos
- ✅ Transferencias internacionales
- ✅ Contacto con autoridades

## 🔄 **Actualizar Aplicación**

Después de personalizar:

1. **Reconstruir imagen Docker:**
   ```bash
   docker build -t quickbooks-app .
   ```

2. **Probar localmente:**
   ```bash
   docker run -p 8000:8000 quickbooks-app
   # Visitar: http://localhost:8000/terms
   # Visitar: http://localhost:8000/privacy
   ```

3. **Desplegar en producción:**
   ```bash
   ./deploy.sh
   ```

## ✅ **Verificación**

Antes de configurar QuickBooks, verifica:

- [ ] Todas las páginas cargan correctamente
- [ ] Información de contacto es correcta
- [ ] Emails de contacto funcionan
- [ ] URLs son accesibles vía HTTPS
- [ ] Contenido es apropiado para tu negocio

## 🎯 **URLs Finales para QuickBooks**

Una vez todo configurado, usa estas URLs en QuickBooks Developer:

```
End-user License Agreement URL: https://tu-dominio-real.com/terms
Privacy Policy URL: https://tu-dominio-real.com/privacy
```

¡Con estas páginas legales tu aplicación cumplirá los requisitos de QuickBooks para producción! 🎉