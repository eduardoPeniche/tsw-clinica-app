from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from clinica_app.domain.exceptions import ValidacionDominioError


@dataclass
class Paciente:
    nombre: str
    fecha_nacimiento: date
    contacto: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValidacionDominioError("El nombre del paciente es obligatorio.")
        if self.fecha_nacimiento > date.today():
            raise ValidacionDominioError(
                "La fecha de nacimiento no puede estar en el futuro."
            )
        if not self.contacto.strip():
            raise ValidacionDominioError("El contacto del paciente es obligatorio.")
