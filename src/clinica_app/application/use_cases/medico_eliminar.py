from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import MedicoRepository


class EliminarMedico:
    def __init__(self, repositorio: MedicoRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, medico_id: UUID) -> None:
        if not self.repositorio.eliminar(medico_id):
            raise RecursoNoEncontradoError("El médico no existe.")
