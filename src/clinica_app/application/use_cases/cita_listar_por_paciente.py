from uuid import UUID

from clinica_app.application.ports import CitaRepository
from clinica_app.domain.entities import Cita


class ListarCitasPorPaciente:
    def __init__(self, repositorio: CitaRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, paciente_id: UUID) -> list[Cita]:
        return self.repositorio.listar_por_paciente(paciente_id)
