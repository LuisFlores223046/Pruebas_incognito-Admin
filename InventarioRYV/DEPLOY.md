# Despliegue en PythonAnywhere — RYV Rentas

## Pasos para poner el sistema en producción (gratis)

### 1. Crear cuenta
Registrarse en https://www.pythonanywhere.com (plan gratuito Beginner)

### 2. Abrir consola Bash
En el dashboard de PythonAnywhere → "Consoles" → "Bash"

### 3. Clonar el repositorio
```bash
git clone <url-del-repositorio> ryv_rentas
cd ryv_rentas
```

### 4. Crear entorno virtual
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 5. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 6. Crear archivo .env
```bash
cat > .env << 'EOF'
SECRET_KEY=cambia-esto-por-una-clave-secreta-larga-y-aleatoria
PYTHONANYWHERE_HOST=tuusuario.pythonanywhere.com
DB_PATH=/home/tuusuario/ryv_rentas/db.sqlite3
EOF
```

> Reemplaza `tuusuario` con tu nombre de usuario de PythonAnywhere.
> Genera una SECRET_KEY segura con:
> `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 7. Aplicar migraciones
```bash
python manage.py migrate --settings=config.settings.production
```

### 8. Recolectar archivos estáticos
```bash
python manage.py collectstatic --settings=config.settings.production --noinput
```

### 9. Crear administrador inicial
```bash
python manage.py crear_admin_inicial --settings=config.settings.production
```
Usuario: `admin` / Contraseña: `Admin1234!`
**Cambia la contraseña inmediatamente después del primer inicio de sesión.**

### 10. Configurar la aplicación web en PythonAnywhere

1. En el dashboard → "Web" → "Add a new web app"
2. Seleccionar "Manual configuration" → Python 3.11
3. En la sección **"Code"**:
   - Source code: `/home/tuusuario/ryv_rentas`
   - Working directory: `/home/tuusuario/ryv_rentas`
4. En la sección **"Virtualenv"**:
   - `/home/tuusuario/ryv_rentas/venv`
5. En la sección **"WSGI configuration file"**, reemplazar todo el contenido con:

```python
import os
import sys

path = '/home/tuusuario/ryv_rentas'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. En la sección **"Static files"**:
   - URL: `/static/`
   - Directory: `/home/tuusuario/ryv_rentas/staticfiles`

7. Hacer clic en **"Reload"**

### 11. Verificar
Navegar a `https://tuusuario.pythonanywhere.com` — el sistema debe estar activo.

## Actualizaciones futuras

```bash
cd ~/ryv_rentas
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --settings=config.settings.production --noinput
# Recargar la app desde el dashboard de PythonAnywhere
```

## Notas importantes

- La base de datos SQLite se guarda en la ruta especificada en `DB_PATH`
- Los archivos estáticos compilados están en `staticfiles/`
- Los logs de error están en el dashboard de PythonAnywhere → "Web" → "Log files"
- El plan gratuito de PythonAnywhere tiene límite de ancho de banda pero es suficiente para uso interno (3 personas)
