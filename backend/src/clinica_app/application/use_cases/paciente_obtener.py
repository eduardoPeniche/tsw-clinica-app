from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import PacienteRepository
from clinica_app.domain.entities import Paciente


class ObtenerPaciente:
    def __init__(self, repositorio: PacienteRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, paciente_id: UUID) -> Paciente:
        paciente = self.repositorio.obtener_por_id(paciente_id)
        if paciente is None:
            raise RecursoNoEncontradoError("El paciente no existe.")
        return paciente
