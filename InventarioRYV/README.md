# RYV Rentas — Sistema de Control de Inventario y Rentas

Sistema web en Django para gestionar equipos, rentas, pagos y devoluciones.

---

## Instalación

**Requisitos:** Python 3.11+ y Git instalados.

```bash
# 1. Clonar y entrar al repositorio
git clone <url-del-repositorio>
cd Pruebas_incognito-Admin

# 2. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r InventarioRYV\requirements.txt
```

---

## Configuración

Crea el archivo `InventarioRYV\.env` con este contenido:

```env
SECRET_KEY=django-insecure-ryv-rentas-local-dev
PYTHONANYWHERE_HOST=tuusuario.pythonanywhere.com
DB_PATH=db.sqlite3
```

---

## Primer arranque

```bash
cd InventarioRYV
python manage.py makemigrations
python manage.py migrate
python manage.py crear_admin_inicial
python manage.py runserver
```

Abre **http://127.0.0.1:8000**

| Usuario | Contraseña |
|---------|-----------|
| `admin` | `Admin1234!` |

> Cambia la contraseña después del primer inicio de sesión.

---

## Roles

| Rol | Puede hacer |
|-----|-------------|
| **Administrador** | Todo: crear/editar equipos, registrar y finalizar rentas, aprobar solicitudes, ver reportes |
| **Empleado** | Consultar inventario y rentas, enviar solicitudes al administrador |

---

## Módulos

| Módulo | Ruta | Descripción |
|--------|------|-------------|
| Inventario | `/inventario/` | Equipos disponibles, en renta y en mantenimiento |
| Rentas activas | `/rentas/` | Rentas en curso con alertas de vencimiento |
| Historial | `/historial/` | Rentas finalizadas con detalle de pagos |
| Solicitudes | `/panel/solicitudes/` | Aprobación de solicitudes de empleados |
| Reportes | `/reportes/` | PDFs de rentas activas e ingresos |
| Panel admin | `/panel/` | Dashboard, usuarios y solicitudes |

---

## Flujo básico

**Registrar una renta (admin):**
1. Rentas → Nueva renta
2. Agrega uno o varios equipos con sus cantidades
3. Llena datos del cliente, fechas, precio y depósito (mínimo 50%)
4. Selecciona método de pago → Registrar

**Finalizar una renta (admin):**
1. Rentas activas → Ver / Finalizar
2. Selecciona la condición del equipo devuelto
3. Si hay daños, ingresa el cargo adicional
4. Si hay saldo pendiente, ingresa el monto recibido y método de pago
5. Confirmar devolución → las unidades se liberan automáticamente

**Como empleado:** en lugar de ejecutar acciones directamente, usa los botones
"Solicitar" — el administrador aprueba o rechaza desde el panel.

---

## Producción (PythonAnywhere)

Ver [`DEPLOY.md`](./DEPLOY.md) para instrucciones completas.

---

## Problemas frecuentes

**"No module named django"** → activa el venv: `venv\Scripts\activate`

**Cambios en modelos no aplicados** → `python manage.py makemigrations && python manage.py migrate`

**Olvidé la contraseña del admin** → `python manage.py changepassword admin`

**Puerto ocupado** → `python manage.py runserver 8080`
