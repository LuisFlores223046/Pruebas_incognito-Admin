# RYV Rentas — Sistema de Control de Inventario y Rentas

Sistema web desarrollado en Django para gestionar el inventario de equipos y herramientas,
el registro de rentas, pagos, devoluciones y el flujo de aprobación entre empleados y administradores.

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación local (Windows)](#2-instalación-local-windows)
3. [Configuración del archivo .env](#3-configuración-del-archivo-env)
4. [Primer arranque](#4-primer-arranque)
5. [Acceso al sistema](#5-acceso-al-sistema)
6. [Roles y permisos](#6-roles-y-permisos)
7. [Módulos del sistema](#7-módulos-del-sistema)
8. [Flujo de trabajo completo](#8-flujo-de-trabajo-completo)
9. [Despliegue en producción (PythonAnywhere)](#9-despliegue-en-producción-pythonanywhere)
10. [Solución de problemas frecuentes](#10-solución-de-problemas-frecuentes)

---

## 1. Requisitos previos

Antes de instalar el proyecto asegúrate de tener instalado:

| Herramienta | Versión mínima | Descarga |
|-------------|---------------|----------|
| Python | 3.11 | https://www.python.org/downloads/ |
| Git | cualquiera | https://git-scm.com/downloads |

> **Windows:** al instalar Python marca la casilla **"Add Python to PATH"**.

---

## 2. Instalación local (Windows)

### 2.1 Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Pruebas_incognito-Admin
```

### 2.2 Crear el entorno virtual

```bash
python -m venv venv
```

### 2.3 Activar el entorno virtual

```bash
venv\Scripts\activate
```

> Sabrás que está activo cuando veas `(venv)` al inicio de la línea en la terminal.
> **Cada vez que abras una nueva terminal debes activar el venv antes de cualquier comando.**

### 2.4 Instalar las dependencias

```bash
pip install -r InventarioRYV\requirements.txt
```

---

## 3. Configuración del archivo .env

El proyecto requiere un archivo `.env` dentro de la carpeta `InventarioRYV/`.
Copia el archivo de ejemplo y edítalo:

```bash
copy InventarioRYV\.env.example InventarioRYV\.env
```

Abre `InventarioRYV\.env` y configura los valores:

```env
SECRET_KEY=django-insecure-ryv-rentas-local-dev-cambia-en-produccion
PYTHONANYWHERE_HOST=tuusuario.pythonanywhere.com
DB_PATH=db.sqlite3
```

> Para desarrollo local los valores del ejemplo funcionan tal cual.
> En producción genera una `SECRET_KEY` segura con:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 4. Primer arranque

Ejecuta estos comandos **en orden** desde la carpeta raíz del repositorio
(`Pruebas_incognito-Admin`) con el entorno virtual activado:

```bash
# 1. Entrar a la carpeta del proyecto
cd InventarioRYV

# 2. Crear las tablas de la base de datos
python manage.py makemigrations
python manage.py migrate

# 3. Crear el usuario administrador inicial
python manage.py crear_admin_inicial

# 4. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 5. Iniciar el servidor de desarrollo
python manage.py runserver
```

Abre tu navegador en: **http://127.0.0.1:8000**

### Credenciales del administrador inicial

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Contraseña | `Admin1234!` |

> **Cambia la contraseña inmediatamente después del primer inicio de sesión.**

---

## 5. Acceso al sistema

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000/` | Página principal / inicio de sesión |
| `http://127.0.0.1:8000/inventario/` | Lista de equipos |
| `http://127.0.0.1:8000/rentas/` | Rentas activas |
| `http://127.0.0.1:8000/historial/` | Historial de rentas finalizadas |
| `http://127.0.0.1:8000/reportes/` | Reportes en PDF |
| `http://127.0.0.1:8000/panel/` | Panel de administración |

---

## 6. Roles y permisos

El sistema tiene dos roles de usuario:

### Administrador
- Registra, edita y da de baja equipos directamente
- Crea y finaliza rentas directamente
- Aprueba o rechaza solicitudes de empleados
- Accede a reportes PDF de ingresos
- Gestiona usuarios del sistema
- Ve el panel de administración completo

### Empleado
- Consulta el inventario y las rentas activas
- Envía **solicitudes** al administrador para:
  - Registrar una nueva renta
  - Cerrar una renta activa
  - Dar de alta, editar o dar de baja un equipo
- No puede ejecutar acciones directamente; todo pasa por aprobación

### Crear un nuevo usuario

1. Inicia sesión como administrador
2. Ve a **Panel de administración → Usuarios → Nuevo usuario**
3. Completa nombre, usuario, contraseña y asigna el rol

---

## 7. Módulos del sistema

### 7.1 Inventario

**Ruta:** `/inventario/`

Gestiona todos los equipos y herramientas disponibles para renta.

**Campos de cada equipo:**
- Nombre y descripción
- Cantidad total / en renta / en mantenimiento
- Imagen de referencia (opcional)
- Estado calculado automáticamente: Disponible, Parcialmente disponible, Todo rentado, En mantenimiento

**Acciones disponibles (admin):**
- **Nuevo equipo:** registra una herramienta con su cantidad total
- **Editar:** modifica nombre, descripción, cantidades
- **Dar de baja:** desactiva el equipo (solo si no tiene rentas activas)
- **Solicitar cambio (empleado):** envía una solicitud de alta/edición/baja al administrador

---

### 7.2 Rentas

**Ruta:** `/rentas/`

Gestiona el ciclo completo de una renta: creación, seguimiento y cierre.

**Crear una renta (admin) — campos:**
- **Equipos a rentar:** puedes agregar uno o varios equipos con sus cantidades (clic en "+ Agregar equipo")
- **Datos del cliente:** nombre, teléfono, dirección, correo
- **Fechas:** inicio y vencimiento
- **Precio total**
- **Depósito:** mínimo el 50% del precio total (obligatorio)
- **Método de pago del depósito:** Efectivo / Transferencia / Tarjeta / Otro (obligatorio si el depósito > $0)
- **Notas** (opcional)

**Estados de una renta:**
| Estado | Descripción |
|--------|-------------|
| Activa | En curso |
| Finalizada | Devuelta y cerrada correctamente |
| Vencida | Superó la fecha de vencimiento sin devolverse |

**Colores en la lista:**
- Fondo rojo → renta vencida
- Fondo amarillo → vence en 3 días o menos

---

### 7.3 Finalizar una renta

Desde el detalle de una renta activa, el administrador completa el formulario de devolución:

1. **Condición del equipo al devolver** (obligatorio):
   - Bueno — sin daños
   - Daños menores
   - Inservible / Pérdida total
   - Extraviado

2. **Cargo por daños** (obligatorio si la condición no es "Bueno"):
   - Monto adicional a cobrar al cliente

3. **Liquidación automática:**
   - El sistema calcula: `Saldo a cobrar = Precio − Depósito + Cargo por daños`
   - Si el depósito ya cubre todo: se muestra "El depósito ya cubre el total"
   - Si hay saldo pendiente: aparece el campo de monto recibido

4. **Monto recibido** (obligatorio si hay saldo pendiente):
   - Debe ser mayor o igual al saldo a cobrar
   - El sistema calcula automáticamente el cambio a devolver

5. **Método de pago al cierre** (obligatorio si hay saldo pendiente)

> El empleado no puede finalizar rentas directamente. Debe enviar una **solicitud de cierre**
> y el administrador la aprueba desde el panel, lo que lo redirige al formulario de devolución.

---

### 7.4 Historial

**Ruta:** `/historial/`

Lista todas las rentas finalizadas con sus detalles completos:
- Equipo(s), cliente, fechas
- Desglose de pagos: precio, depósito, cargo por daños, monto recibido, cambio entregado
- Condición de devolución con color indicativo
- Filtros por cliente, equipo y rango de fechas

---

### 7.5 Solicitudes (flujo empleado → admin)

**Ruta empleado:** visible desde inventario y rentas con botones "Solicitar"
**Ruta admin:** `/panel/solicitudes/`

Cuando un empleado no puede ejecutar una acción directamente, genera una solicitud:

| Tipo de solicitud | Qué hace |
|-------------------|----------|
| Alta de equipo | Propone registrar un nuevo equipo |
| Edición de equipo | Propone cambiar datos de un equipo |
| Baja de equipo | Propone desactivar un equipo |
| Nueva renta | Propone registrar una renta con sus datos |
| Cierre de renta | Propone cerrar una renta activa |

El administrador ve la solicitud con todos los datos capturados y puede:
- **Aprobar:** ejecuta la acción automáticamente
- **Rechazar:** descarta la solicitud con un comentario

---

### 7.6 Reportes

**Ruta:** `/reportes/`

Genera reportes en PDF descargables:

- **Reporte de rentas activas:** lista completa con estado, equipos y saldos
- **Reporte de ingresos:** rentas finalizadas con desglose de pagos, depósitos, cargos por daños y totales

---

### 7.7 Panel de administración

**Ruta:** `/panel/`

Exclusivo para administradores. Contiene:
- Dashboard con métricas: equipos disponibles, rentas activas, vencidas, próximas a vencer
- Gestión de usuarios: crear, editar rol, activar/desactivar
- Lista de solicitudes pendientes con vista de tarjetas

---

## 8. Flujo de trabajo completo

### Caso 1: Renta nueva (admin)
```
1. Inventario → selecciona equipo → "Rentar"
2. Completa datos del cliente, fechas, precio, depósito y método de pago
3. Agrega más equipos si es necesario con "+ Agregar equipo"
4. Clic en "Registrar renta" → queda en estado Activa
```

### Caso 2: Renta nueva (empleado)
```
1. Inventario → "Solicitar renta" o Rentas → "Solicitar renta"
2. Completa todos los campos + comentario para el admin
3. El admin recibe la solicitud en el panel y la aprueba
4. La renta queda registrada automáticamente
```

### Caso 3: Devolver un equipo (admin)
```
1. Rentas activas → clic en "Ver / Finalizar" en la renta correspondiente
2. Selecciona la condición del equipo
3. Si hay daños, ingresa el cargo por daños
4. Si hay saldo pendiente, ingresa el monto recibido del cliente
5. Selecciona el método de pago
6. Clic en "Confirmar devolución"
7. Las unidades del equipo quedan liberadas automáticamente
```

### Caso 4: Devolver un equipo (empleado)
```
1. Rentas activas → clic en "Solicitar cierre" en la renta correspondiente
2. Escribe un comentario descriptivo
3. El admin aprueba la solicitud desde el panel
4. El sistema lleva al admin directamente al formulario de devolución
```

---

## 9. Despliegue en producción (PythonAnywhere)

Ver instrucciones detalladas en [`DEPLOY.md`](./DEPLOY.md).

Resumen rápido:
```bash
# En la consola Bash de PythonAnywhere
git clone <url-del-repositorio> InventarioRYV
cd InventarioRYV
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Crear .env con valores de producción
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --settings=config.settings.production --noinput
python manage.py crear_admin_inicial --settings=config.settings.production
```

---

## 10. Solución de problemas frecuentes

### "No module named django"
El entorno virtual no está activado. Ejecuta:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### "No migrations to apply" con advertencia de cambios pendientes
```bash
python manage.py makemigrations
python manage.py migrate
```

### La página de estilos no carga (solo texto plano)
```bash
python manage.py collectstatic --noinput
```
Asegúrate de que `DEBUG = True` en desarrollo o que WhiteNoise esté configurado en producción.

### Error al subir imágenes de equipos
Verifica que existe la carpeta `media/` dentro de `InventarioRYV/`:
```bash
mkdir InventarioRYV\media
```

### Olvidé la contraseña del administrador
```bash
cd InventarioRYV
python manage.py changepassword admin
```

### El servidor no inicia por puerto ocupado
```bash
python manage.py runserver 8080
# Luego entra a http://127.0.0.1:8080
```

---

## Stack tecnológico

| Componente | Tecnología |
|------------|-----------|
| Backend | Django 4.2 |
| Base de datos | SQLite (desarrollo) |
| Archivos estáticos | WhiteNoise |
| Generación de PDF | ReportLab |
| Imágenes | Pillow |
| Configuración | python-decouple |
| Servidor WSGI | Gunicorn (producción) |
