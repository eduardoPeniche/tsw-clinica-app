# Sistema de gestión de citas médicas

## Propósito del proyecto

Construir el esqueleto funcional de una aplicación para gestionar pacientes,
médicos y sus citas. El proyecto servirá como base para practicar decisiones de
arquitectura, persistencia, pruebas automatizadas y despliegue con Docker.

Este documento es el registro vivo del proyecto: además de describir lo que se
debe construir, irá documentando las decisiones tomadas, su justificación y el
estado de cada requisito.

## Alcance de la primera entrega

Para la próxima sesión, el repositorio debe poder levantarse con un único
comando (`docker-compose up`) y ofrecer las operaciones mínimas indicadas más
abajo. La interfaz web es opcional; la API o el mecanismo elegido debe quedar
operativo y verificable.

## Modelo funcional

### Pacientes

Se debe administrar la información básica de cada paciente:

| Campo | Descripción |
| --- | --- |
| Nombre | Nombre completo del paciente. |
| Fecha de nacimiento | Fecha de nacimiento del paciente. |
| Contacto | Medio de contacto, por ejemplo teléfono o correo electrónico. |

Operaciones requeridas: crear, consultar, listar, actualizar y eliminar
pacientes.

### Médicos

Se debe administrar la información básica de cada médico:

| Campo | Descripción |
| --- | --- |
| Nombre | Nombre completo del médico. |
| Especialidad | Área médica en la que atiende. |

Operaciones requeridas: crear, consultar, listar, actualizar y eliminar
médicos.

### Citas

Cada cita relaciona a un paciente con un médico en una fecha y hora definidas.

| Campo | Descripción |
| --- | --- |
| Paciente | Paciente que recibirá la atención. |
| Médico | Médico que brindará la atención. |
| Fecha y hora | Momento programado para la cita. |
| Estado | `pendiente`, `confirmada` o `cancelada`. |

Operaciones requeridas:

- Crear una cita.
- Cancelar una cita.
- Consultar las citas asignadas a un médico.
- Consultar las citas de un paciente.

## Regla de negocio prioritaria

No se debe permitir registrar una cita cuando el médico ya tiene otra cita en
el mismo horario.

Esta regla debe validarse antes de crear la cita y, cuando exista un conflicto,
el sistema debe responder de manera clara para que la persona usuaria entienda
que el horario no está disponible. La definición concreta del horario, el
tratamiento de citas canceladas, la protección ante solicitudes simultáneas y
la ubicación de la validación dentro de la arquitectura se documentarán como
decisiones del proyecto.

## Requisitos técnicos obligatorios

- El backend se implementará en Python. Se puede usar FastAPI u otro framework
  que permita ejecutar pruebas automatizadas.
- Los datos deben almacenarse de forma persistente; una base de datos SQLite es
  una opción válida para el inicio.
- El proyecto incluirá un `Dockerfile` y un `docker-compose.yml` para levantar
  la solución con un solo comando.
- El código se controlará con Git mediante commits pequeños e incrementales que
  reflejen avances reales.
- El repositorio incluirá un `README.md` con los requisitos y pasos necesarios
  para ejecutar el proyecto.

## Decisiones abiertas

Estas decisiones se resolverán durante el desarrollo y su resultado quedará
registrado aquí.

| Tema | Decisión | Justificación | Estado |
| --- | --- | --- | --- |
| Framework del backend | FastAPI `0.141.1` con Python 3.14. | Permite crear una API en Python y ejecutar pruebas automatizadas. | Aceptada |
| Representación de entidades | `dataclasses` de Python con identificadores UUID. | Reduce código repetitivo y mantiene las entidades independientes de frameworks y de la persistencia. | Aceptada |
| Definición de puertos | `Protocol` de Python. | Los adaptadores cumplen el contrato por sus métodos, sin heredar de una clase base. | Aceptada |
| Motor y modelo de persistencia | SQLite mediante `sqlite3`. | Persistencia real sin agregar dependencias. | Aceptada |
| Organización de capas y carpetas | Arquitectura hexagonal organizada por tipo técnico. | Hace explícitos los límites entre entidades, casos de uso, puertos y adaptadores; es adecuada para aprender este estilo. | Aceptada |
| Organización de casos de uso | Un archivo por acción del sistema. | Mantiene cada operación pequeña, explícita y fácil de probar. | Aceptada |
| Nombres de casos de uso | Patrón `entidad_accion`, por ejemplo `paciente_crear.py`. | Mantiene los archivos agrupados visualmente por entidad dentro de la capa técnica `use_cases`. | Aceptada |
| Cancelación de citas | Operación idempotente. | Repetir una cancelación deja la cita en estado `cancelada` sin generar error. | Aceptada |
| Diseño de la API | API REST con rutas HTTP para pacientes, médicos y citas; la disponibilidad se consulta mediante un recurso específico por médico y fecha. | Mantiene las operaciones CRUD explícitas y permite que el backend entregue al frontend el estado de cada slot sin trasladarle reglas de agenda. | Aceptada |
| Duración y formato de los horarios | Slots de 30 minutos, de lunes a viernes, entre 09:00 y 17:00 de `America/Merida`. El último inicio permitido es 16:30. | Mantiene una agenda predecible y hace explícitos los límites que se deben validar. | Aceptada |
| Citas que bloquean un horario | Las citas `pendiente` y `confirmada` bloquean el slot; una cita `cancelada` lo libera. | Corresponde a los estados definidos para el modelo de citas. | Aceptada |
| Estrategia contra citas simultáneas | Validación de intervalo en el caso de uso y un índice único parcial de SQLite como respaldo para inicios idénticos activos. | Protege el caso básico de esta entrega. Una garantía completa ante concurrencia y traslapes arbitrarios se reconsiderará al migrar a un motor con restricciones de intervalos, como PostgreSQL. | Aceptada para la primera entrega |
| Frontend | Astro con HTML, CSS y TypeScript nativos, dentro de `frontend/`. | Es liviano para esta entrega, permite una interfaz funcional sin introducir un framework de componentes adicional y se integra con los tipos generados desde OpenAPI. | Aceptada |
| Ejecución en contenedor | Imagen Python 3.14 con dependencias sincronizadas mediante `uv` dentro de Docker. | Permite ejecutar el proyecto sin instalar dependencias Python en el equipo local. | Aceptada |

## Plan de avance

| Hito | Resultado esperado | Estado |
| --- | --- | --- |
| 1. Base del proyecto | Repositorio Git, estructura inicial y documentación. | Completado |
| 2. Entidades y persistencia | Modelos y base de datos persistente para pacientes, médicos y citas. | Completado |
| 3. CRUD principal | Operaciones completas de pacientes y médicos. | Completado |
| 4. Gestión de citas | Creación, cancelación y consultas por médico o paciente. | Completado |
| 5. Validación de agenda | Primera implementación de la regla de disponibilidad del médico. | Completado |
| 6. Entorno reproducible | Docker, Docker Compose, pruebas y README de ejecución. | Completado |

## Bitácora de decisiones

Agregaremos aquí cada acuerdo relevante con fecha, contexto y consecuencia en
la implementación.

| Fecha | Decisión | Contexto y justificación |
| --- | --- | --- |
| 2026-09-18 | Se adopta arquitectura hexagonal organizada por tipo técnico. | La regla de disponibilidad de citas debe poder probarse sin depender de FastAPI ni SQLite. Esta variante hace visibles sus límites principales. El detalle está en `docs/adr/001-arquitectura-hexagonal.md`. |
| 2026-09-18 | Se organizarán los casos de uso en un archivo por acción. | Por ejemplo, `crear_cita.py` y `cancelar_cita.py` serán independientes. |
| 2026-09-19 | Los archivos de casos de uso usarán el patrón `entidad_accion`. | Por ejemplo, `paciente_crear.py` y `medico_eliminar.py`; todos permanecen en `application/use_cases`. |
| 2026-09-19 | La cancelación de citas será idempotente. | Una cita ya cancelada permanece cancelada si la operación se repite. |
| 2026-09-19 | Se adopta FastAPI `0.141.1` con Python 3.14. | Es el framework seleccionado para el backend. |
| 2026-09-19 | El proyecto se ejecutará con Docker Compose. | El contenedor usa Python 3.14 y `uv sync --frozen` para instalar dentro de la imagen las versiones fijadas en `uv.lock`. |
| 2026-09-19 | Las entidades de dominio usarán `dataclasses` e identificadores UUID. | Permite modelarlas con Python estándar sin acoplarlas al ORM o a FastAPI. |
| 2026-09-19 | Los puertos de repositorio usarán `Protocol`. | Los adaptadores SQLite y los repositorios falsos de pruebas no tendrán que heredar de una clase abstracta. |
| 2026-09-19 | La agenda clínica atiende de lunes a viernes de 09:00 a 17:00, en slots de 30 minutos y zona `America/Merida`. | El último inicio válido es 16:30. La política de dominio valida estas condiciones antes de comprobar la disponibilidad del médico. El detalle está en `docs/adr/002-politica-de-agenda.md`. |
| 2026-09-19 | La API expone recursos REST para pacientes, médicos y citas, además de disponibilidad por médico y fecha. | La agenda cruda se conserva para mostrar y cancelar citas; el recurso de disponibilidad devuelve slots libres, ocupados o no disponibles, y evita duplicar reglas de negocio en el frontend. |
| 2026-09-19 | El frontend se implementa con Astro, HTML, CSS y TypeScript nativos. | Vive en `frontend/`, se inicia junto al backend mediante Docker Compose en desarrollo y consume la API mediante un proxy `/api`. |
| 2026-09-19 | La concurrencia se cubre hasta el alcance de SQLite para la primera entrega. | El caso de uso verifica traslapes activos y SQLite mantiene un índice parcial para impedir dos citas activas con el mismo médico e inicio. Una garantía transaccional completa queda fuera del alcance actual. |

## Criterios de aceptación de la primera entrega

- La aplicación inicia usando `docker-compose up`.
- Pacientes y médicos se pueden crear, consultar, listar, actualizar y eliminar.
- Se pueden crear y cancelar citas.
- Se pueden consultar las citas de un paciente y las asignadas a un médico.
- El sistema rechaza, al menos en el caso básico, una segunda cita para un mismo
  médico en la misma fecha y hora.
- La ejecución del proyecto está explicada en el `README.md`.
