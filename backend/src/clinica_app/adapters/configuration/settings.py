from dataclasses import dataclass
from datetime import datetime, time, timedelta
import os
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class AgendaSettings:
    dias_atencion: frozenset[int]
    hora_apertura: time
    hora_cierre: time
    duracion_cita: timedelta
    zona_horaria: ZoneInfo


def _hora(variable: str, default: str) -> time:
    value = os.getenv(variable, default)
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as error:
        raise ValueError(f"{variable} debe tener el formato HH:MM.") from error


def _dias_atencion() -> frozenset[int]:
    value = os.getenv("APPOINTMENT_WEEKDAYS", "0,1,2,3,4")
    try:
        dias = frozenset(int(day) for day in value.split(","))
    except ValueError as error:
        raise ValueError("APPOINTMENT_WEEKDAYS debe ser una lista de días entre 0 y 6.") from error

    if not dias or not dias.issubset(range(7)):
        raise ValueError("APPOINTMENT_WEEKDAYS debe contener días entre 0 y 6.")
    return dias


def agenda_settings_from_environment() -> AgendaSettings:
    duration = int(os.getenv("APPOINTMENT_DURATION_MINUTES", "30"))
    if duration <= 0:
        raise ValueError("APPOINTMENT_DURATION_MINUTES debe ser mayor que cero.")

    return AgendaSettings(
        dias_atencion=_dias_atencion(),
        hora_apertura=_hora("APPOINTMENT_OPENING_TIME", "09:00"),
        hora_cierre=_hora("APPOINTMENT_CLOSING_TIME", "17:00"),
        duracion_cita=timedelta(minutes=duration),
        zona_horaria=ZoneInfo(os.getenv("CLINIC_TIME_ZONE", "America/Merida")),
    )
