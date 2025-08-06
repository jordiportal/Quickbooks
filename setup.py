"""
Script de configuración rápida para QuickBooks Online
"""

import os
import shutil
import subprocess
import sys

def main():
    """Configuración automática del proyecto"""
    print("🚀 Configurando integración con QuickBooks Online...")
    print()
    
    # Verificar Python
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        return False
    
    print("✅ Python version:", sys.version.split()[0])
    
    # Instalar dependencias
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False
    
    # Crear archivo .env si no existe
    if not os.path.exists('.env'):
        if os.path.exists('config.env.example'):
            shutil.copy('config.env.example', '.env')
            print("✅ Archivo .env creado desde ejemplo")
        else:
            create_env_file()
    else:
        print("ℹ️  Archivo .env ya existe")
    
    # Mostrar siguiente paso
    print()
    print("🎉 ¡Configuración completada!")
    print()
    print("📋 Próximos pasos:")
    print("1. Ve a https://developer.intuit.com/ y crea una aplicación")
    print("2. Edita el archivo .env con tus credenciales:")
    print("   - QB_CLIENT_ID (desde QuickBooks Developer)")
    print("   - QB_CLIENT_SECRET (desde QuickBooks Developer)")
    print("3. Ejecuta: python app.py")
    print("4. Visita: http://localhost:5000")
    print()
    
    return True

def create_env_file():
    """Crea archivo .env básico"""
    env_content = """# Configuración de QuickBooks Online
QB_CLIENT_ID=tu_client_id_aqui
QB_CLIENT_SECRET=tu_client_secret_aqui
QB_REDIRECT_URI=http://localhost:5000/callback
QB_SANDBOX_BASE_URL=https://sandbox-quickbooks.api.intuit.com
QB_DISCOVERY_URL=https://appcenter.intuit.com/connect/oauth2/.well-known/openid_configuration

# Configuración de la aplicación
SECRET_KEY=clave_secreta_por_defecto_cambiar_en_produccion
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado")

if __name__ == "__main__":
    main()