from uuid import UUID

from clinica_app.application.ports import CitaRepository
from clinica_app.domain.entities import Cita


class ListarCitasPorMedico:
    def __init__(self, repositorio: CitaRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, medico_id: UUID) -> list[Cita]:
        return self.repositorio.listar_por_medico(medico_id)
