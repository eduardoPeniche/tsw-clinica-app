from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CitaInput(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    fecha_hora: datetime


class CitaOutput(CitaInput):
    id: UUID
    estado: str
