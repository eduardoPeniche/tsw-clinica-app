from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import MedicoRepository
from clinica_app.domain.entities import Medico


class ActualizarMedico:
    def __init__(self, repositorio: MedicoRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(
        self,
        medico_id: UUID,
        nombre: str,
        especialidad: str,
    ) -> Medico:
        if self.repositorio.obtener_por_id(medico_id) is None:
            raise RecursoNoEncontradoError("El médico no existe.")

        medico = Medico(nombre, especialidad, id=medico_id)
        return self.repositorio.actualizar(medico)
