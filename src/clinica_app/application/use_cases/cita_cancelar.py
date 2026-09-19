from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import CitaRepository
from clinica_app.domain.entities import Cita


class CancelarCita:
    def __init__(self, repositorio: CitaRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, cita_id: UUID) -> Cita:
        cita = self.repositorio.obtener_por_id(cita_id)
        if cita is None:
            raise RecursoNoEncontradoError("La cita no existe.")

        cita.cancelar()
        return self.repositorio.actualizar(cita)
