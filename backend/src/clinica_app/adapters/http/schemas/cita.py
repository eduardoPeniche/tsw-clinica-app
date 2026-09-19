from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class CitaInput(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    fecha_hora: datetime


class CitaOutput(CitaInput):
    id: UUID
    estado: str


class SlotDisponibilidadOutput(BaseModel):
    inicio: str
    fin: str
    estado: Literal["libre", "ocupado"]


class DisponibilidadAgendaOutput(BaseModel):
    fecha: date
    zona_horaria: str
    slots: list[SlotDisponibilidadOutput]
    slot_recomendado: str | None
