# ProQuim Gestión

Sistema integral de gestión de producción e inventario para una empresa de productos químicos, desarrollado para la materia de Diseño de Sistemas de Información.

## Integrantes

- Johan David Ramirez Giraldo
- Mateo Sandoval Montoya
- Xiomara Cetre Mosquera
- Norman Santiago Echavarría Fonnegra

**Curso:** 580304012-3 Diseño de Sistemas de Información  
**Docente:** Alexandra Guerrero Bocanegra  
**Instituto:** Instituto Tecnológico Metropolitano — 2026-1

---

## ¿Qué es esto?

Sistema web que permite gestionar recetas químicas, validar compatibilidad entre sustancias, ejecutar órdenes de producción, controlar inventario y generar reportes. Implementa una arquitectura en capas (Controladores → Servicios → Repositorios → SQLite) con patrones de diseño GoF y principios SOLID.

---

## Requisitos

- Python 3.10 o superior
- pip

---

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install flask reportlab

# 2. Ejecutar
python app.py

# 3. Abrir en el navegador
http://127.0.0.1:5000
```

> La base de datos SQLite (`database/proquim.db`) se crea automáticamente al primer arranque. Si existe una versión anterior, borrarla antes de correr la app para que se regenere con los datos correctos.

---

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| admin | admin123 | Administrador |
| jefe | jefe123 | Jefe de Producción |
| operario | operario123 | Operario |
| gerente | gerente123 | Gerente |
| inventario | inv123 | Responsable de Inventario |

Las contraseñas se almacenan con hash SHA-256. El login valida credenciales reales contra la base de datos.

---

## Control de acceso por rol

Cada rol solo ve y puede acceder a las secciones que le corresponden:

| Sección | Administrador | Jefe de Producción | Operario | Gerente | Resp. Inventario |
|---|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Recetas | ✅ | ✅ | ❌ | ❌ | ❌ |
| Órdenes | ✅ | ✅ | ✅ | ❌ | ❌ |
| Inventario | ✅ | ❌ | ❌ | ❌ | ✅ |
| Reportes | ✅ | ✅ | ❌ | ✅ | ✅ |
| Configuración | ✅ | ❌ | ❌ | ❌ | ❌ |

El control se aplica tanto en el menú (frontend) como en las rutas del backend (`@requiere_rol`).

---

## Funcionalidades

- **Recetas técnicas:** creación con ingredientes, gramajes y validación química automática
- **Validación de compatibilidad química:** detecta y bloquea combinaciones peligrosas (ej. alcohol etílico + hipoclorito de sodio)
- **Órdenes de producción:** creación, ejecución con descuento automático de stock y registro de trazabilidad
- **Control de inventario:** stock actual, stock mínimo, alertas automáticas cuando el stock baja del mínimo
- **Trazabilidad:** historial completo de cada lote producido (orden, receta, consumos, responsable, fecha)
- **Reportes:** estadísticas de producción con exportación a CSV y PDF real

---

## Patrones de diseño GoF implementados

| # | Patrón | Tipo | Módulo | Función |
|---|---|---|---|---|
| 1 | Singleton | Creacional | `database/connection.py` | Una única instancia de conexión a SQLite |
| 2 | Factory Method | Creacional | `patrones.py` → `ReporteFactory` | Creación desacoplada de tipos de reporte |
| 3 | Observer | Comportamiento | `patrones.py` → `observable_inventario` | Notificación automática cuando el stock baja |
| 4 | Strategy | Comportamiento | `patrones.py` → `ValidadorQuimico` | Intercambio dinámico de algoritmos de validación química |
| 5 | Decorator | Estructural | `patrones.py` → `ReporteDecorator` | Extensión de reportes con exportación PDF/Excel |

---

## Principios SOLID

| Principio | Nivel | Evidencia |
|---|---|---|
| SRP | Alto | Cada clase tiene una única responsabilidad (controlador, servicio, repositorio) |
| OCP | Alto | Nuevas validaciones y reportes se agregan sin modificar clases existentes |
| LSP | Alto | Subclases de Strategy e IReportable respetan los contratos abstractos |
| ISP | Medio-Alto | Interfaces cohesionadas y específicas por módulo |
| DIP | Medio-Alto | `IDatabaseConnection` desacopla repositorios de la implementación concreta |

---

## Arquitectura

El sistema sigue el modelo C4 con una arquitectura en capas:

```
Interfaz Web (HTML/CSS/JS)
        ↓ JSON / HTTPS
Controladores (Flask Blueprints)
  auth_controller · recetas_controller · ordenes_controller
  inventario_controller · trazabilidad_controller · reportes_controller
        ↓
Servicios (lógica de negocio)
  AuthService · RecetaService · ValidacionQuimicaService
  OrdenProduccionService · InventarioService · TrazabilidadService · ReporteService
        ↓
Repositorios (acceso a datos)
  UsuarioRepository · RecetaRepository · QuimicoRepository · OrdenRepository
        ↓
Base de datos SQLite
```

---

## Estructura de archivos

```
ProQuim/
├── app.py                        # Entrada principal, registro de blueprints y guards de rol
├── patrones.py                   # Los 5 patrones GoF implementados
├── requirements.txt              # Flask, reportlab
├── database/
│   ├── connection.py             # Singleton + IDatabaseConnection (DIP)
│   ├── db.py                     # init_db()
│   └── schema.sql                # Esquema y datos iniciales
├── controllers/                  # Capa de controladores (Blueprints)
│   ├── auth_controller.py
│   ├── recetas_controller.py
│   ├── ordenes_controller.py
│   ├── inventario_controller.py
│   ├── trazabilidad_controller.py
│   └── reportes_controller.py
├── services/                     # Capa de servicios (lógica de negocio)
│   ├── auth_service.py
│   ├── receta_service.py
│   ├── validacion_quimica_service.py
│   ├── orden_produccion_service.py
│   ├── inventario_service.py
│   ├── trazabilidad_service.py
│   └── reporte_service.py
├── repositories/                 # Capa de repositorios (acceso a BD)
│   ├── usuario_repository.py
│   ├── receta_repository.py
│   ├── quimico_repository.py
│   └── orden_repository.py
├── templates/                    # HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── recetas.html
│   ├── ordenes_produccion.html
│   ├── inventario.html
│   ├── reportes.html
│   ├── configuracion.html
│   └── error.html
└── static/
    ├── css/styles.css
    └── js/main.js
```

---

## Dependencias

```
Flask==3.1.0
reportlab==4.2.5
```

Instalación:
```bash
pip install flask reportlab
```