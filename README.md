# Sistema de gestión de citas médicas

## Estructura

```text
backend/   API FastAPI, SQLite, pruebas y dependencias Python
frontend/  Interfaz web Astro
```

La [guía de arquitectura](docs/arquitectura.md) explica la organización del
backend. Las decisiones y sus consecuencias están en los [ADR](docs/adr/).

## Ejecutar con Docker

La aplicación se ejecuta desde un contenedor; no es necesario instalar las
dependencias de Python en el equipo local.

```bash
docker compose up --build
```

Compose es el entorno de desarrollo: ambos servicios observan los cambios en
sus carpetas de código y se recargan automáticamente. Para imágenes de
producción se usarán los Dockerfiles directamente, sin los montajes de código.

La API queda disponible en `http://localhost:8000`; la documentación
interactiva está en `http://localhost:8000/docs`.

El frontend Astro queda disponible en `http://localhost:4321` por defecto. Si
alguno de los puertos del equipo está ocupado, copia `.env.example` como `.env`
y cambia `BACKEND_PORT` o `FRONTEND_PORT`. Los servicios conservan sus puertos
internos (`8000` y `4321`), por lo que su comunicación dentro de Docker no
cambia. También se pueden definir solo para una ejecución:

```bash
BACKEND_PORT=8001 FRONTEND_PORT=4322 docker compose up --build
```

Con ese ejemplo, Swagger quedará en `http://localhost:8001/docs` y el frontend
en `http://localhost:4322`.

## Ejecutar pruebas

```bash
docker compose run --rm -e NOTIFICATION_WEBHOOK_URL= backend python -m unittest discover -s tests
```

`NOTIFICATION_WEBHOOK_URL` se vacía para que las pruebas no envíen eventos a
n8n aunque esté configurado en `.env`.

## Generar tipos del frontend

Para ejecutar el frontend fuera de Docker, copia `frontend/.env.example` como
`frontend/.env`. Ahí se configura tanto el proxy de desarrollo hacia el backend
como la URL para generar los tipos. Con la API levantada, genera los tipos
TypeScript desde OpenAPI:

```bash
cd frontend
OPENAPI_URL=http://localhost:8000/openapi.json npm run generate:api
```

Si se configuró un `BACKEND_PORT` distinto para Docker, usa ese mismo puerto en
`frontend/.env` o en `OPENAPI_URL`.

Dentro de Docker, ambas variables apuntan automáticamente al servicio `backend`.
El archivo generado se versiona y se regenera cuando cambian los esquemas de
FastAPI.

## Automatizaciones con n8n

`docker compose up --build` también levanta n8n, ya configurado. El backend le
envía un evento cada vez que se crea o se cancela una cita, y n8n publica un
aviso en el canal de Discord de recepción: una tarjeta verde para una cita
nueva y una roja para una cancelada. La decisión está en el
[ADR 004](docs/adr/004-notificaciones-n8n.md).

El editor queda en `http://localhost:5678` (solo desde el equipo local), con la
cuenta de demostración:

| Usuario | Contraseña |
|---|---|
| `recepcion@example.com` | `ClinicaDemo2026` |

En cada arranque, `n8n/arranque.sh` registra la credencial de Discord e importa
y publica `n8n/workflows/clinica-eventos.json` antes de iniciar n8n. No hay
pasos manuales, pero el flujo del repositorio reemplaza los cambios hechos en
el editor. Para conservarlos, expórtalos antes de reiniciar:

```bash
docker compose run --rm --entrypoint n8n n8n export:workflow --id=ClinicaEventos01 --pretty --output=/n8n/workflows/clinica-eventos.json
```

El evento tiene esta forma (`evento` es `cita_creada` o `cita_cancelada`):

```json
{
  "evento": "cita_creada",
  "cita": { "id": "…", "fecha_hora": "2026-11-04T10:00:00-06:00", "estado": "pendiente" },
  "paciente": { "id": "…", "nombre": "Ana López", "contacto": "ana@example.com" },
  "medico": { "id": "…", "nombre": "Dr. Ruiz", "especialidad": "Cardiología" }
}
```

Cancelar de nuevo una cita ya cancelada no genera otro evento. Si n8n no
responde, la cita se registra igual y el error aparece en el log del backend.
Desde n8n, la API se consulta en `http://backend:8000`.

La URL del webhook de Discord está en `docker-compose.yml` y es pública:
cualquiera que la tenga puede publicar en el canal. Para usar otro canal,
define `DISCORD_WEBHOOK_URL` en `.env`. Para proteger el webhook de n8n, define
`NOTIFICATION_WEBHOOK_TOKEN` y configura en el nodo Webhook la autenticación
*Header Auth* con el encabezado `X-Clinica-Token`.

## Análisis de seguridad

Los informes están en [`zap/informe.html`](zap/informe.html) y
[`burp/informe.html`](burp/informe.html). Los reportes crudos y las capturas
están en `zap/reportes/`, `zap/evidencia/` y `burp/evidencia/`.

### OWASP ZAP

`zap/compose.yml` levanta un backend de producción con base de datos temporal
y ejecuta ZAP contra su definición OpenAPI. No toca los datos de desarrollo.

```bash
mkdir -p zap/reportes/antes
FASE=antes docker compose -f zap/compose.yml --profile scan run --rm zap-pasivo
FASE=antes docker compose -f zap/compose.yml --profile scan run --rm zap-activo
docker compose -f zap/compose.yml down -v
```

La variable `FASE` define la carpeta de salida (`antes` o `despues`). Cada
ejecución genera un reporte en HTML, JSON y Markdown.

### Burp Suite

`burp/compose.yml` levanta dos versiones del sistema para comparar sus
respuestas HTTP. La versión `antes` usa el commit `af3b590`, anterior a la
corrección de encabezados. Construye su imagen una vez:

```bash
git archive af3b590:backend | docker build --target production -t clinica-backend:antes -
docker compose -f burp/compose.yml up -d --build
docker compose -f burp/compose.yml down -v
```

| Versión | Frontend | Backend |
|---|---|---|
| `antes` | `http://localhost:4322` | `http://localhost:8001` |
| `despues` | `http://localhost:4323` | `http://localhost:8002` |

Abre el navegador integrado de Burp Suite (Proxy → Open browser) y usa ambos
frontends. Burp se ejecuta fuera de Docker.

## MCP por stdio

El adaptador MCP es opcional: no inicia con `docker compose up` ni publica un
puerto. Un host MCP local debe iniciarlo como proceso hijo mediante:

```bash
docker compose --profile mcp run --rm -T mcp
```

Mientras la sesión del agente esté abierta, ese proceso reutiliza los casos de
uso existentes para administrar pacientes, médicos y citas. Comparte el volumen
SQLite con el backend, pero no expone SQL ni rutas HTTP como herramientas.

### Configuración compartida para agentes

El repositorio incluye un lanzador portable en `scripts/run-mcp`, que encuentra
la raíz del proyecto y crea un contenedor MCP temporal. No depende de la ruta
donde cada integrante haya clonado el repositorio.

- Codex carga `.codex/config.toml` al abrir un proyecto confiable. Las
  herramientas de consulta son de solo lectura; las que modifican datos
  requieren aprobación.
- Claude Code carga `.mcp.json` y solicita aprobar el servidor de proyecto la
  primera vez.
- Grok Build carga `.grok/config.toml`. También reconoce `.mcp.json` por
  compatibilidad, pero la configuración nativa tiene prioridad.

En ambos casos, abre el agente desde la raíz del repositorio con Docker u
OrbStack en ejecución. El agente inicia una sola instancia MCP durante la
sesión; no se crea un contenedor por cada herramienta utilizada.

Para un host que no reconozca esos archivos, ejecuta manualmente:

```bash
sh ./scripts/run-mcp
```
