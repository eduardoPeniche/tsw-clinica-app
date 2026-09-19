from uuid import UUID

from pydantic import BaseModel


class MedicoInput(BaseModel):
    nombre: str
    especialidad: str


class MedicoOutput(MedicoInput):
    id: UUID
