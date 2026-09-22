# ADR 003: Adaptador MCP local por stdio

- Estado: Aceptada
- Fecha: 2026-09-21

## Contexto

Además de la API HTTP, se desea que un agente compatible con Model Context
Protocol (MCP) pueda consultar disponibilidad y administrar citas. El agente no
debe acceder directamente a SQLite ni repetir las validaciones de horario.

## Decisión

Se agrega `adapters/mcp/server.py` como adaptador de entrada. Usa el SDK oficial
`mcp[cli]`, fijado en el grupo opcional `mcp` de `uv`. El servidor se comunica
por `stdio`: el host MCP lo inicia como proceso hijo y conserva la conexión
durante toda la sesión del agente.

El servicio Compose `mcp` pertenece al perfil `mcp`; por eso no inicia con
`docker compose up` y no publica puertos. El host puede iniciarlo mediante:

```bash
docker compose --profile mcp run --rm -T mcp
```

Para compartir el arranque entre integrantes sin rutas absolutas, el repositorio
incluye `scripts/run-mcp`. El lanzador localiza su propia carpeta, resuelve la
raíz del proyecto y ejecuta el comando anterior. Cada host usa el formato de
configuración que reconoce, pero invoca el mismo lanzador:

- `.codex/config.toml` para Codex.
- `.mcp.json` para Claude Code.
- `.grok/config.toml` para Grok Build.

Los archivos de configuración no contienen credenciales. Un host debe tratar
el proyecto como confiable antes de ejecutar un servidor `stdio` definido por
el repositorio.

El adaptador construye el mismo `ApplicationContainer` que usa FastAPI y expone
estas herramientas:

- `listar_pacientes`
- `crear_paciente`, `actualizar_paciente`, `eliminar_paciente`
- `listar_medicos`
- `crear_medico`, `actualizar_medico`, `eliminar_medico`
- `consultar_disponibilidad`
- `crear_cita`
- `cancelar_cita`

Las herramientas de consulta se anuncian como solo lectura. Las de creación,
actualización, eliminación y cancelación indican al agente que confirme los
datos con la persona usuaria antes de ejecutarlas.

```text
Host MCP → stdio → adapters/mcp/server.py → casos de uso → puertos → SQLite
FastAPI  → HTTP  → adapters/http/         → casos de uso → puertos → SQLite
```

## Consecuencias

- FastAPI y MCP comparten reglas de negocio, política de agenda y volumen
  SQLite; el adaptador MCP no usa SQL ni rutas HTTP.
- Las notificaciones se envían por el puerto `NotificationSender`; el adaptador
  de consola escribe en `stderr` para no interferir con `stdio` cuando MCP crea
  una cita.
- El grupo `mcp` se instala en los objetivos Docker `development` y `mcp`, pero
  no en el objetivo `production`.
- Cada sesión de agente crea un proceso MCP temporal, no un contenedor por cada
  llamada de herramienta.
- MCP no define un archivo de descubrimiento universal: la comunicación sí es
  interoperable, pero cada host conserva su propia política de configuración y
  aprobación.
- La solución es apropiada para uso local. Si se expone por red en el futuro,
  se deberá usar Streamable HTTP con autenticación y autorización antes de
  manejar datos de pacientes.
