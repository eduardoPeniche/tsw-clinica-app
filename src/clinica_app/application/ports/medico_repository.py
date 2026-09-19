from typing import Protocol
from uuid import UUID

from clinica_app.domain.entities import Medico


class MedicoRepository(Protocol):
    """Operaciones de persistencia que requieren los casos de uso de médicos."""

    def guardar(self, medico: Medico) -> Medico: ...

    def obtener_por_id(self, medico_id: UUID) -> Medico | None: ...

    def listar(self) -> list[Medico]: ...

    def actualizar(self, medico: Medico) -> Medico: ...

    def eliminar(self, medico_id: UUID) -> bool: ...
