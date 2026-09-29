# Arquitectura del backend

El backend usa arquitectura hexagonal. Los [ADR](adr/) registran las decisiones;
esta guía explica cómo se organizan sus componentes.

## Por qué se llama «hexagonal»

El nombre viene del diagrama de Alistair Cockburn: cada lado del hexágono
representa una forma de conectar la aplicación con el exterior. No exige seis
componentes. FastAPI y MCP son adaptadores de entrada; SQLite y la salida de
notificaciones son adaptadores de salida.

```text
FastAPI / MCP → casos de uso → puertos → SQLite / notificaciones
                    ↓
                  dominio
```

## Organización del código

`backend/src/clinica_app/` se divide por responsabilidad:

- `domain/`: entidades, excepciones y política de agenda; no importa
  infraestructura.
- `application/use_cases/`: operaciones como crear una cita. Coordina el dominio
  y usa los contratos de `application/ports/`.
- `application/ports/`: interfaces de repositorios y notificaciones expresadas
  con `Protocol`.
- `adapters/`: rutas HTTP, servidor MCP, configuración, SQLite y notificaciones.
- `container.py`: construye los adaptadores y los inyecta en los casos de uso.

## Comparación con módulos funcionales

Organizar por módulos funcionales y usar arquitectura hexagonal responde a dos
preguntas distintas: cómo se agrupan los archivos y hacia dónde apuntan las
dependencias. Para esta aplicación se eligió una estructura por tipo técnico
que hace visibles los límites hexagonales.

| Aspecto | Módulos funcionales simples | Estructura hexagonal elegida |
| --- | --- | --- |
| Organización | Cada área reúne rutas, servicios y persistencia. | Se separan dominio, casos de uso, puertos y adaptadores. |
| Dependencias | Un servicio puede importar directamente un repositorio o el ORM. | Los casos de uso dependen de puertos; los adaptadores implementan esos contratos. |
| Pruebas | Probar un servicio puede requerir preparar la base de datos. | Un adaptador en memoria permite probar los casos de uso de forma aislada. |
| Cambio de interfaz o base de datos | Puede afectar el servicio del módulo. | Se cambia el adaptador correspondiente si el puerto sigue siendo válido. |
| Costo inicial | Menos archivos y contratos. | Más archivos y contratos explícitos. |

En una estructura por módulos funcionales simples, cada área agrupa sus
componentes:

```text
app/
  pacientes/
    routes.py
    service.py
    repository.py
  medicos/
    routes.py
    service.py
    repository.py
  citas/
    routes.py
    service.py
    repository.py
  database.py
```

Por ejemplo, `citas/routes.py` recibe la solicitud, `citas/service.py` valida
el horario y `citas/repository.py` consulta y guarda en SQLite. Es una
estructura directa para un sistema pequeño. Si el servicio importa el
repositorio concreto, la validación queda ligada a la persistencia.

La estructura actual agrupa primero por responsabilidad técnica:

```text
clinica_app/
  domain/
    entities/
    policies/
  application/
    use_cases/
    ports/
  adapters/
    http/
    mcp/
    persistence/sqlite/
  container.py
```

Así, `application/use_cases/cita_crear.py` aplica la política y consulta el
puerto `application/ports/cita_repository.py`. El repositorio SQLite implementa
el puerto desde `adapters/persistence/sqlite/`. Las rutas HTTP y el servidor MCP
invocan el mismo caso de uso.

También es posible agrupar por área *dentro* de cada zona hexagonal. Si el
sistema crece, `application/use_cases/` podría tener carpetas `pacientes/`,
`medicos/` y `citas/` sin cambiar la dirección de las dependencias.

## Dirección de las dependencias

Al implementar una operación, el dominio define las reglas y los casos de uso
definen qué necesitan del exterior mediante puertos. Después, los adaptadores
cumplen esos contratos:

```text
Dominio → puertos y casos de uso → adaptadores → composición en container.py
```

Esta es una secuencia de construcción, no la dirección de los imports. El
dominio no importa FastAPI, MCP ni SQLite. Los casos de uso importan entidades y
puertos. Los adaptadores implementan esos contratos por su estructura, sin
necesidad de importarlos. `container.py` conecta las implementaciones concretas
con los casos de uso.

## Ejemplo: crear una cita

Una ruta HTTP o una herramienta MCP entrega los datos a `CrearCita`. El caso de
uso comprueba que existan el paciente y el médico, aplica `PoliticaAgenda` y
consulta mediante `CitaRepository` si el intervalo se solapa con otra cita
activa. Si está libre, guarda la cita y envía una notificación mediante otro
puerto. El adaptador SQLite implementa la persistencia. Las reglas no viven en
el transporte ni en el repositorio.

## Por qué los puertos usan `Protocol`

Una clase abstracta exige que el adaptador herede explícitamente de ella.
`Protocol` permite definir un contrato por su estructura: una clase con los
métodos y firmas requeridos puede satisfacerlo sin heredar del puerto.

```python
from typing import Protocol
from clinica_app.domain.entities import Paciente

class PacienteRepository(Protocol):
    def guardar(self, paciente: Paciente) -> Paciente: ...

class SQLitePacienteRepository:
    def guardar(self, paciente: Paciente) -> Paciente:
        ...
```

El adaptador SQLite y uno en memoria para pruebas pueden cumplir el mismo
puerto. Un analizador de tipos puede detectar firmas incompatibles; Python no
valida automáticamente el contrato al crear el objeto.
