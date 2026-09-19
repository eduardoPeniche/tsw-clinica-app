from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class EstadoCita(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


@dataclass
class Cita:
    paciente_id: UUID
    medico_id: UUID
    fecha_hora: datetime
    estado: EstadoCita = EstadoCita.PENDIENTE
    id: UUID = field(default_factory=uuid4)
