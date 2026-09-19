from datetime import date
from uuid import UUID

from pydantic import BaseModel


class PacienteInput(BaseModel):
    nombre: str
    fecha_nacimiento: date
    contacto: str


class PacienteOutput(PacienteInput):
    id: UUID
