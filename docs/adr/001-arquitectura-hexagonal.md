# ADR 001: Adoptar arquitectura hexagonal

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

La aplicación debe gestionar pacientes, médicos y citas, con una regla de
negocio especialmente importante: un médico no puede tener dos citas en el
mismo horario. Se busca una estructura que permita probar esa regla de forma
aislada y que no mezcle la lógica del negocio con FastAPI o SQLite.

## Decisión

Se adoptará una arquitectura hexagonal, también conocida como *ports and
adapters* (puertos y adaptadores).

La lógica del dominio y los casos de uso no dependerán directamente de FastAPI,
SQLite ni de Docker. En su lugar, se comunicarán con el exterior mediante
contratos llamados **puertos**. Las implementaciones concretas de esos
contratos serán los **adaptadores**.

## Por qué se llama "hexagonal"

El nombre proviene del diagrama usado por Alistair Cockburn para representar
este estilo: la aplicación se dibuja como un hexágono con varios lados. Cada
lado representa una posible forma de conectarse al sistema, no una cantidad
obligatoria de seis componentes.

Por ejemplo, FastAPI puede ser un adaptador de entrada y SQLite un adaptador de
salida. En el futuro, una interfaz web, una línea de comandos o PostgreSQL
podrían conectarse a los mismos casos de uso sin cambiar la lógica central.

```text
FastAPI ──adaptador de entrada──> casos de uso / dominio
                                          │
                                          │ puerto (contrato)
                                          v
                                  adaptador de salida (SQLite)
```

## Comparación evaluada

| Aspecto | Módulos funcionales | Arquitectura hexagonal |
| --- | --- | --- |
| Organización principal | Por área: pacientes, médicos y citas. | Por límites: dominio, casos de uso, puertos y adaptadores. |
| Dependencia de tecnología | Los servicios suelen importar ORM o repositorios concretos. | El núcleo depende de interfaces, no de FastAPI ni de SQLite. |
| Pruebas de reglas de negocio | Requieren más preparación o simulación de infraestructura. | Se prueban con adaptadores falsos, sin levantar API ni base de datos. |
| Complejidad inicial | Menor. | Mayor: requiere definir contratos y adaptadores. |
| Cambio de base de datos o interfaz | Puede afectar servicios y acceso a datos. | Se sustituye principalmente el adaptador correspondiente. |

La organización por módulos funcionales sigue siendo útil dentro de cada zona
de la arquitectura. Por ejemplo, el dominio puede contener `pacientes`,
`medicos` y `citas` sin renunciar a los límites hexagonales.

## Ejemplo de estructura por módulos funcionales

Esta era la alternativa más simple evaluada. Cada área del negocio agrupa sus
rutas, servicios, repositorios y modelos en una misma carpeta:

```text
app/
  pacientes/
    routes.py
    service.py
    repository.py
    models.py
  medicos/
    routes.py
    service.py
    repository.py
    models.py
  citas/
    routes.py
    service.py
    repository.py
    models.py
  database.py
  main.py
```

Al crear una cita, `citas/routes.py` recibiría la solicitud,
`citas/service.py` validaría el horario y `citas/repository.py` consultaría o
guardaría datos en SQLite. Es una estructura clara y adecuada para proyectos
pequeños, aunque sus servicios suelen depender más directamente de detalles de
persistencia.

## Estructura inicial propuesta: organización por tipo técnico

Se utilizará la variante clásica de arquitectura hexagonal. Las carpetas
principales representan responsabilidades técnicas: el dominio, los casos de
uso, los puertos y los adaptadores. Los archivos no se separarán inicialmente
por paciente, médico o cita; se agruparán según la responsabilidad que cumplen.

```text
app/
  main.py                         # Compone la aplicación y sus dependencias.
  domain/                         # Reglas y conceptos puros del negocio.
    entities/
      paciente.py                 # Entidad Paciente.
      medico.py                   # Entidad Medico.
      cita.py                     # Entidad Cita y sus estados.
    exceptions.py                 # Errores de negocio.
  application/                    # Casos de uso; coordina el dominio.
    ports/                        # Contratos que necesita la aplicación.
      paciente_repository.py
      medico_repository.py
      cita_repository.py
    use_cases/                    # Un archivo por acción del sistema.
      paciente_crear.py
      paciente_obtener.py
      paciente_listar.py
      paciente_actualizar.py
      paciente_eliminar.py
      medico_crear.py
      medico_obtener.py
      medico_listar.py
      medico_actualizar.py
      medico_eliminar.py
      cita_crear.py               # Comprueba disponibilidad del médico.
      cita_cancelar.py
      cita_listar_por_medico.py
      listar_citas_por_paciente.py
  adapters/                       # Implementaciones para el mundo exterior.
    http/
      routes/
        pacientes.py              # Endpoints FastAPI de pacientes.
        medicos.py                # Endpoints FastAPI de médicos.
        citas.py                  # Endpoints FastAPI de citas.
      schemas/                    # Modelos de solicitud y respuesta HTTP.
        pacientes.py
        medicos.py
        citas.py
      error_handlers.py           # Convierte errores de negocio a HTTP.
    persistence/
      sqlite/
        database.py               # Configuración de conexión y sesiones.
        models.py                 # Modelos de persistencia/ORM.
        paciente_repository.py    # Implementa el puerto de pacientes.
        medico_repository.py      # Implementa el puerto de médicos.
        cita_repository.py        # Implementa el puerto de citas.
  tests/
    unit/                         # Pruebas de dominio y casos de uso.
    integration/                  # Pruebas de adaptadores y API.
```

Un archivo de caso de uso corresponde a una acción del sistema. Por ejemplo,
`crear_cita.py` recibe los datos necesarios, usa los puertos de repositorio,
valida el horario y devuelve el resultado o un error de negocio. Las rutas
HTTP solo adaptan la petición a ese caso de uso; no contienen la regla de
disponibilidad.

### Flujo de creación de una cita

```text
POST /citas
  → adapters/http/routes/citas.py
  → application/citas/crear_cita.py
  → application/ports/cita_repository.py
  → adapters/persistence/sqlite/cita_repository.py
  → SQLite
```

## Ejemplo: crear una cita

1. Una ruta de FastAPI recibe la solicitud y la convierte a datos del caso de
   uso. No decide si el horario está disponible.
2. El caso de uso `crear_cita` consulta, mediante un puerto, si el médico ya
   tiene una cita activa en esa fecha y hora.
3. Si existe conflicto, el caso de uso devuelve un error de negocio claro.
4. Si no existe conflicto, el caso de uso solicita al puerto guardar la cita.
5. El adaptador de SQLite implementa la consulta y el guardado reales.

## Consecuencias

- La validación de disponibilidad vivirá en el caso de uso de creación de
  citas, por lo que será independiente de HTTP y de SQLite.
- Se crearán pruebas unitarias para los casos de uso usando repositorios falsos
  o simulados.
- Habrá más archivos y contratos que en una solución de capas mínima.
- Será necesario complementar la validación de aplicación con una estrategia
  de persistencia para solicitudes simultáneas; esa decisión queda pendiente.

## Diferencia frente a una organización puramente técnica

Una organización **por tipo técnico** no divide las capas internas por área de
negocio; concentra cada tipo de archivo en una carpeta común:

```text
app/
  domain/
    entities/
      paciente.py
      medico.py
      cita.py
  application/
    use_cases/
      paciente_crear.py
      medico_crear.py
      cita_crear.py
      cita_cancelar.py
    ports/
      paciente_repository.py
      medico_repository.py
      cita_repository.py
  adapters/
    http/
    persistence/
```

La estructura adoptada es la **organización por tipo técnico pura** mostrada
arriba. Esto hace más visible el vocabulario central de la arquitectura
hexagonal —entidades, casos de uso, puertos y adaptadores— y reduce las
decisiones de organización necesarias para esta primera entrega. Si el sistema
crece, se podrá evaluar una organización híbrida sin cambiar esos límites.

## Decisiones de implementación pendientes

| Tema | Pregunta que debemos responder | Estado |
| --- | --- | --- |
| Entidades de dominio | `dataclasses` de Python con identificadores UUID generados en el dominio. | Aceptada |
| Puertos | `Protocol` de Python. | Aceptada |
| Adaptadores iniciales | FastAPI está confirmado para HTTP; falta elegir la biblioteca para SQLite/ORM. | En progreso |
| Dependencias | ¿Desde qué módulo de composición se crearán e inyectarán repositorios y casos de uso? | Pendiente |
| Elementos compartidos | ¿En qué ubicación vivirán configuración, errores generales y utilidades comunes? | Pendiente |
| Concurrencia | ¿Qué mecanismo de base de datos protegerá contra dos reservas simultáneas? | Pendiente |

## Guía de implementación: del dominio a la API

La secuencia de construcción conserva las dependencias hacia el centro de la
arquitectura. No se debe hacer que el dominio o los casos de uso importen
FastAPI, SQLite ni SQL.

```text
Entidades de dominio           ✅
        ↓
Puertos de repositorio         ← siguiente paso
        ↓
Casos de uso CRUD
        ↓
Adaptador SQLite real
        ↓
Rutas HTTP con FastAPI
```

Primero describimos lo que la aplicación necesita para administrar pacientes y
médicos, sin decidir aún cómo se guardan los datos:

```text
application/
  ports/
    paciente_repository.py
    medico_repository.py
    cita_repository.py
  use_cases/
    paciente_crear.py
    paciente_listar.py
    paciente_obtener.py
    paciente_actualizar.py
    paciente_eliminar.py
```

Los archivos de casos de uso siguen el patrón `entidad_accion`. Esto conserva la
organización por tipo técnico —todos pertenecen a `use_cases`— y hace que las
operaciones de cada entidad queden agrupadas visualmente.

Por ejemplo, `PacienteRepository` declara las operaciones `guardar`,
`obtener_por_id`, `listar`, `actualizar` y `eliminar`. El caso de uso
`paciente_crear` depende de ese contrato, no de SQLite.

`CitaRepository` declara las consultas por paciente y médico, además de
`medico_tiene_cita_activa`. El caso de uso `crear_cita` usará esta última
operación para validar disponibilidad antes de guardar una cita.

Después se implementa el adaptador real de persistencia:

```text
adapters/
  persistence/
    sqlite/
      database.py
      paciente_repository.py
      medico_repository.py
```

Ese adaptador cumple los puertos mediante SQLite. Así se obtiene persistencia
real sin introducir SQL en las entidades o en los casos de uso. Finalmente,
las rutas FastAPI son adaptadores de entrada: convierten una petición HTTP en
una llamada a un caso de uso y convierten su resultado en una respuesta HTTP.

La cancelación de una cita será idempotente. El caso de uso obtiene la cita,
invoca `cita.cancelar()` y la actualiza mediante el repositorio. Si la cita ya
estaba cancelada, el método conserva ese estado y no genera un error.

### Por qué usamos `Protocol` para los puertos

Un puerto es una interfaz que especifica los métodos que necesita la
aplicación. En Python se puede expresar mediante una clase abstracta o mediante
`Protocol`.

Una clase abstracta exige que cada adaptador herede explícitamente del
contrato. Python impide instanciar el adaptador si le falta un método abstracto:

```python
from abc import ABC, abstractmethod


class PacienteRepository(ABC):
    @abstractmethod
    def guardar(self, paciente: Paciente) -> Paciente: ...


class SQLitePacienteRepository(PacienteRepository):
    def guardar(self, paciente: Paciente) -> Paciente:
        ...
```

Con `Protocol`, importa la estructura y no la herencia. Cualquier clase que
tenga los métodos con las firmas requeridas puede utilizarse como repositorio:

```python
from typing import Protocol


class PacienteRepository(Protocol):
    def guardar(self, paciente: Paciente) -> Paciente: ...


class SQLitePacienteRepository:
    def guardar(self, paciente: Paciente) -> Paciente:
        ...
```

Esto reduce el acoplamiento: el adaptador SQLite no necesita heredar del puerto
y un repositorio en memoria para pruebas solo necesita implementar los mismos
métodos. Los analizadores de tipos pueden detectar contratos incompletos antes
de ejecutar el programa. Por ese motivo, `Protocol` es la opción elegida para
este proyecto.
