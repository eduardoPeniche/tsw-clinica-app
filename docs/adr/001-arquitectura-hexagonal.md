# ADR 001: Adoptar arquitectura hexagonal

## Estado

Aceptado.

## Contexto

La aplicación gestiona pacientes, médicos y citas. Debe impedir que un médico
tenga citas activas que se solapen. Esta regla requiere pruebas aisladas y no
debe depender de FastAPI ni de SQLite. Una organización por módulos funcionales
sería más simple al inicio, pero facilitaría que los casos de uso dependieran de
la persistencia.

## Decisión

Usaremos arquitectura hexagonal con organización por tipo técnico. El dominio y
los casos de uso dependerán de puertos definidos con `Protocol`; los adaptadores
implementarán esos puertos para HTTP, MCP, persistencia y notificaciones. Las
reglas de negocio permanecerán en el dominio y los casos de uso.

## Consecuencias

- Podremos probar las reglas con adaptadores en memoria y cambiar interfaces o
  persistencia sin modificar los casos de uso.
- Mantendremos más contratos y archivos que en una estructura por módulos
  funcionales simple.
- La validación de disponibilidad en la aplicación no resuelve por sí sola las
  reservas simultáneas; la persistencia también debe proteger esa operación.
