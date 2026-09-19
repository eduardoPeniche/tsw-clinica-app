from datetime import date
from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import PacienteRepository
from clinica_app.domain.entities import Paciente


class ActualizarPaciente:
    def __init__(self, repositorio: PacienteRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(
        self,
        paciente_id: UUID,
        nombre: str,
        fecha_nacimiento: date,
        contacto: str,
    ) -> Paciente:
        if self.repositorio.obtener_por_id(paciente_id) is None:
            raise RecursoNoEncontradoError("El paciente no existe.")

        paciente = Paciente(nombre, fecha_nacimiento, contacto, id=paciente_id)
        return self.repositorio.actualizar(paciente)
