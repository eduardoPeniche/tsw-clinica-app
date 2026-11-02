# Pruebas E2E con Playwright

Este documento describe las pruebas end-to-end de la aplicación de la clínica: qué cubren, cómo están organizadas, cómo ejecutarlas y qué problemas se encontraron al montarlas. Para una introducción general a Playwright, consulta la [guía de Playwright](guia_playwright.md).

## 1. Resumen

- **Herramienta:** Playwright para Python con `pytest-playwright` (Chromium).
- **Alcance:** flujos completos en un navegador real contra la app levantada con Docker (frontend Astro + API FastAPI + SQLite).
- **Estado:** 14 pruebas, todas pasan.
- **Ubicación:** carpeta `e2e/` en la raíz, con su propio entorno virtual, separada del backend y del frontend.

| Archivo | Pruebas | Qué verifica |
|---|---|---|
| `test_navegacion.py` | 2 | Carga inicial y cambio entre Calendario, Pacientes y Médicos. |
| `test_pacientes.py` | 5 | Crear, editar, eliminar, nombre obligatorio y cancelar la eliminación. |
| `test_medicos.py` | 4 | Crear, editar, eliminar y campos obligatorios. |
| `test_citas.py` | 3 | Agendar una cita, cancelarla y comprobar que el hueco ocupado deja de estar libre. |

## 2. Requisitos

- Docker con la app corriendo (`docker compose up -d`): frontend en `http://localhost:4321` y API en `http://localhost:8000`.
- Python 3 en el equipo (se usó 3.13).
- Las pruebas de citas necesitan además que el servicio `backend` de Docker Compose esté activo (ver sección 7).

## 3. Instalación

```bash
cd e2e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-e2e.txt
playwright install chromium
```

`e2e/.venv/` y `e2e/test-results/` están ignorados en Git.

## 4. Estructura

```
e2e/
├── pytest.ini                # URL base, capturas y trazas en fallos
├── conftest.py               # fixtures: API, datos de prueba y limpieza
├── requirements-e2e.txt
├── pages/                    # Page Objects
│   ├── pacientes_page.py
│   ├── medicos_page.py
│   └── calendario_page.py
├── test_navegacion.py
├── test_pacientes.py
├── test_medicos.py
├── test_citas.py
└── grabaciones/              # borradores generados con codegen (no se ejecutan)
```

### Configuración (`pytest.ini`)

```ini
[pytest]
testpaths = .
addopts = --base-url=http://localhost:4321 --screenshot=only-on-failure --tracing=retain-on-failure --output=test-results
norecursedirs = grabaciones .venv test-results
```

### Fixtures principales (`conftest.py`)

| Fixture | Función |
|---|---|
| `browser_context_args` | Viewport 1280×800, idioma `es-MX` y zona horaria `America/Merida`. |
| `api` | Cliente HTTP contra la API (`E2E_API_URL`, por defecto `http://localhost:8000`) para preparar y limpiar datos. |
| `nombre_unico` | Nombre irrepetible (`E2E Paciente <uuid>`) para no chocar entre corridas. |
| `paciente_api`, `medico_api` | Crean un paciente o médico por API y lo borran al terminar. |
| `limpiar_pacientes`, `limpiar_medicos` | Borran todo lo que empiece por `E2E ` al terminar. |
| `pausa_final` | Espera `E2E_PAUSA_FINAL` ms al final de cada prueba (0 por defecto); sirve para los videos. |

## 5. Cómo ejecutar

```bash
docker compose up -d                    # app arriba
cd e2e && source .venv/bin/activate

pytest                                  # todas, sin ventana (headless)
pytest test_pacientes.py                # un archivo
pytest -k "cancelar"                    # por nombre
pytest --headed                         # con el navegador visible
pytest --headed --slowmo 700            # visible y más lento
```

## 6. Grabar videos y generar pruebas

### Generar una prueba a partir de tus acciones (`codegen`)

Playwright no convierte un video en pruebas. Lo que sí hace es registrar tus acciones y escribir el código:

```bash
playwright codegen --target python-pytest -o test_grabado.py http://localhost:4321
```

Lo grabado es solo un borrador. Para convertirlo en una prueba válida hay que:

1. Darle un nombre descriptivo y quitar imports que no se usen.
2. Reemplazar datos fijos por nombres únicos y añadir limpieza.
3. Aceptar o cancelar el `confirm()` nativo cuando se elimina o cancela algo.
4. Reemplazar índices como `.nth(2)` por filtros por texto.
5. **Añadir aserciones (`expect`)**: sin ellas la prueba solo hace clics y nunca falla.

El primer borrador de este proyecto está en `e2e/grabaciones/` como referencia; de él salió `test_cancelar_eliminacion_conserva_paciente`.

### Grabar video de la ejecución

```bash
E2E_PAUSA_FINAL=2500 pytest --video=on --slowmo 700
open test-results/*/video.webm          # ver todos los videos
```

- `--video=on` guarda un `video.webm` por prueba en `e2e/test-results/<prueba>/`.
- `--slowmo 700` pausa 700 ms tras cada acción de Playwright para poder seguirla.
- `E2E_PAUSA_FINAL=2500` deja 2.5 s con el resultado en pantalla al final.
- `test-results/` se **vacía en cada corrida**: si ejecutas sin `--video=on`, los videos anteriores se pierden. Copia los que quieras conservar.
- Playwright no genera un solo video con todas las pruebas; habría que unirlos con una herramienta externa como `ffmpeg`.

### Depurar una falla

Si una prueba falla, `pytest.ini` ya guarda captura de pantalla y traza:

```bash
playwright show-trace test-results/<prueba>/trace.zip
PWDEBUG=1 pytest -s test_citas.py       # Inspector paso a paso
```

## 7. Decisiones y problemas resueltos

### Hidratación de React
Las vistas de Pacientes y Médicos usan `client:visible`: el botón "Agregar" aparece antes de que la página sea interactiva y un clic temprano se pierde. Los Page Objects esperan a que desaparezca el texto "Cargando…", que solo ocurre cuando React ya cargó los datos.

### Cuadros `confirm()` nativos
Eliminar un paciente o médico y cancelar una cita usan `confirm()`. Se manejan con `page.once("dialog", ...)` antes del clic (`accept()` para confirmar, `dismiss()` para cancelar).

### Datos de prueba y limpieza
Los datos se crean con prefijo `E2E ` y un identificador único, y se borran al terminar cada prueba.

**Bug del backend:** borrar un paciente o médico que tiene citas devuelve `500 Internal Server Error` (la clave foránea de `citas` lo impide y el backend no lo maneja), y la API no tiene endpoint para borrar citas. Para no dejar basura, la limpieza elimina primero las citas E2E directamente en SQLite con:

```bash
docker compose exec -T backend python -c "..."
```

Por eso las pruebas de citas requieren Docker. Pendiente recomendado: que la API responda `409` con un mensaje claro en lugar de `500`.

### Calendario
- Las pruebas de citas usan la vista **Día** y eligen el primer hueco libre, sin depender de una fecha fija.
- Una cita nueva queda en estado `pendiente`.
- El `aria-label` de cada hueco ("ocupado, fecha, de X a Y") reemplaza su texto visible como nombre accesible, así que se localizan por ese prefijo (`^libre`, `^ocupado`).
- La tabla de citas queda bajo el calendario, fuera de los 800 px del viewport. Los tests llaman a `mostrar_citas()` para que el resultado aparezca en el video.

### Video de "cancelar cita" que parecía no cancelar
La prueba sí cancelaba, pero el video terminaba con el calendario y sin mostrar la tabla ni el aviso. Se resolvió desplazando la vista a la tabla al final y con la pausa final opcional.

## 8. Cómo agregar una prueba nueva

1. Graba el flujo con `playwright codegen` para obtener los localizadores.
2. Si la página es nueva, crea su Page Object en `e2e/pages/`.
3. Escribe la prueba usando nombres únicos y las fixtures de limpieza.
4. Prefiere `get_by_role` y `get_by_label` antes que selectores CSS.
5. Termina siempre con `expect(...)`; no uses `time.sleep()`.
6. Ejecuta `pytest` y verifica que no queden datos `E2E ` en la API.

## 9. Pendientes

- Vistas Semana y Mes del calendario, y navegación entre periodos.
- Pruebas de errores del backend (por ejemplo, cita en un horario ya ocupado).
- Integración con GitHub Actions (no incluida; ver el ejemplo en la [guía](guia_playwright.md#12-integración-con-docker-y-ci)).
- Corregir en el backend el `500` al borrar pacientes o médicos con citas.
