from datetime import datetime
from typing import Protocol
from uuid import UUID

from clinica_app.domain.entities import Cita


class CitaRepository(Protocol):
    """Operaciones de persistencia que requieren los casos de uso de citas."""

    def guardar(self, cita: Cita) -> Cita: ...

    def obtener_por_id(self, cita_id: UUID) -> Cita | None: ...

    def listar_por_medico(self, medico_id: UUID) -> list[Cita]: ...

    def listar_por_paciente(self, paciente_id: UUID) -> list[Cita]: ...

    def actualizar(self, cita: Cita) -> Cita: ...

    def medico_tiene_cita_activa(
        self,
        medico_id: UUID,
        fecha_hora: datetime,
    ) -> bool: ...
