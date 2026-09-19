from dataclasses import dataclass, field
from uuid import UUID, uuid4

from clinica_app.domain.exceptions import ValidacionDominioError


@dataclass
class Medico:
    nombre: str
    especialidad: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValidacionDominioError("El nombre del médico es obligatorio.")
        if not self.especialidad.strip():
            raise ValidacionDominioError("La especialidad del médico es obligatoria.")
