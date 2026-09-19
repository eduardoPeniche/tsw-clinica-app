from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import MedicoRepository
from clinica_app.domain.entities import Medico


class ObtenerMedico:
    def __init__(self, repositorio: MedicoRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, medico_id: UUID) -> Medico:
        medico = self.repositorio.obtener_por_id(medico_id)
        if medico is None:
            raise RecursoNoEncontradoError("El médico no existe.")
        return medico
