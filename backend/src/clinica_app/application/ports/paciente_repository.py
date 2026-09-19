from typing import Protocol
from uuid import UUID

from clinica_app.domain.entities import Paciente


class PacienteRepository(Protocol):
    """Operaciones de persistencia que requieren los casos de uso de pacientes."""

    def guardar(self, paciente: Paciente) -> Paciente: ...

    def obtener_por_id(self, paciente_id: UUID) -> Paciente | None: ...

    def listar(self) -> list[Paciente]: ...

    def actualizar(self, paciente: Paciente) -> Paciente: ...

    def eliminar(self, paciente_id: UUID) -> bool: ...
