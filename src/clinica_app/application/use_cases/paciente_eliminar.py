from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import PacienteRepository


class EliminarPaciente:
    def __init__(self, repositorio: PacienteRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, paciente_id: UUID) -> None:
        if not self.repositorio.eliminar(paciente_id):
            raise RecursoNoEncontradoError("El paciente no existe.")
