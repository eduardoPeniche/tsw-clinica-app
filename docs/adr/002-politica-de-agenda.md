# ADR 002: Política de agenda clínica

- Estado: Aceptada
- Fecha: 2026-09-19

## Contexto

La disponibilidad de un médico es la regla de negocio prioritaria del sistema.
La regla original evitaba únicamente dos citas activas con la misma fecha y
hora, pero no definía cuándo atiende la clínica ni la duración de cada cita.

## Decisión

La clínica atenderá de lunes a viernes, de 09:00 a 17:00, en la zona horaria
`America/Merida`. Cada cita dura 30 minutos y debe iniciar en un slot de media
hora. Por tanto, el primer inicio válido es 09:00 y el último es 16:30.

Las variables de entorno del adaptador de configuración permiten declarar esos
valores para cada despliegue:

```text
CLINIC_TIME_ZONE=America/Merida
APPOINTMENT_WEEKDAYS=0,1,2,3,4
APPOINTMENT_OPENING_TIME=09:00
APPOINTMENT_CLOSING_TIME=17:00
APPOINTMENT_DURATION_MINUTES=30
```

`AgendaSettings` lee esas variables y el contenedor construye una
`PoliticaAgenda`. La política es un `dataclass(frozen=True)` del dominio: no
importa FastAPI, SQLite ni variables de entorno. El caso de uso `CrearCita` la
ejecuta antes de comprobar y guardar la disponibilidad del médico.

Las horas sin zona enviadas por el formulario se interpretan como hora local de
la clínica. El dominio las normaliza con `America/Merida` y SQLite guarda su
representación ISO 8601 con offset.

```text
FastAPI → CrearCita → PoliticaAgenda → repositorio de citas → SQLite
```

## Consecuencias

- Una fecha de sábado/domingo, fuera de 09:00–17:00 o que no caiga en un slot
  válido devuelve un error de validación de dominio, traducido a HTTP `422`.
- Una cita activa del mismo médico en un slot válido continúa devolviendo HTTP
  `409`. La aplicación compara intervalos completos, por lo que también
  detecta citas históricas creadas fuera de un slot, por ejemplo una cita a las
  11:01 que se cruza con los slots 11:00–11:30 y 11:30–12:00. El índice único
  parcial de SQLite mantiene una protección adicional para inicios alineados
  idénticos.
- El frontend etiqueta las entradas como hora de Mérida y presenta las citas
  con esa zona, aunque el navegador use otra distinta.
- La consulta de agenda acepta una fecha (`GET /medicos/{id}/citas?fecha=…`)
  para que el frontend muestre las citas reales del día. La disponibilidad se
  consulta por separado (`GET /medicos/{id}/disponibilidad?fecha=…`): el
  backend devuelve los slots libres u ocupados y el recomendado, sin duplicar
  reglas de agenda en el frontend.
- El selector de fecha del frontend ofrece únicamente los próximos 60 días
  laborables de Mérida; el backend conserva la validación para cualquier otro
  cliente de la API.
