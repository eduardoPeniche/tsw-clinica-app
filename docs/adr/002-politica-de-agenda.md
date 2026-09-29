# ADR 002: Definir la política de agenda clínica

## Estado

Aceptado.

## Contexto

Impedir citas simultáneas para un médico no define cuándo atiende la clínica ni
la duración de una consulta. La API y el frontend necesitan una misma regla de
disponibilidad y una zona horaria explícita.

## Decisión

Usaremos la zona `America/Merida`. La clínica atenderá de lunes a viernes, de
09:00 a 17:00, con citas de 30 minutos que comenzarán cada media hora; el último
inicio válido será a las 16:30. Configuraremos estos valores por despliegue y
aplicaremos la política en el dominio antes de comprobar la disponibilidad del
médico. Interpretaremos las horas sin zona como hora local de la clínica.

## Consecuencias

- Rechazaremos horarios fuera de la política con un error de validación y los
  solapamientos con un error de conflicto.
- Calcularemos la disponibilidad en el backend para que todos los clientes
  reciban la misma regla.
- El frontend mostrará los horarios en la zona de la clínica, aunque el
  navegador use otra zona.
- Los cambios de horario o duración requerirán configurar cada despliegue y
  mantener coherentes las citas existentes.
