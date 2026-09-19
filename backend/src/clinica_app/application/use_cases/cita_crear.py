from datetime import datetime
from uuid import UUID

from clinica_app.application.exceptions import (
    HorarioNoDisponibleError,
    RecursoNoEncontradoError,
)
from clinica_app.application.ports import (
    CitaRepository,
    MedicoRepository,
    PacienteRepository,
)
from clinica_app.domain.entities import Cita


class CrearCita:
    def __init__(
        self,
        cita_repositorio: CitaRepository,
        paciente_repositorio: PacienteRepository,
        medico_repositorio: MedicoRepository,
    ) -> None:
        self.cita_repositorio = cita_repositorio
        self.paciente_repositorio = paciente_repositorio
        self.medico_repositorio = medico_repositorio

    def ejecutar(
        self,
        paciente_id: UUID,
        medico_id: UUID,
        fecha_hora: datetime,
    ) -> Cita:
        if self.paciente_repositorio.obtener_por_id(paciente_id) is None:
            raise RecursoNoEncontradoError("El paciente no existe.")
        if self.medico_repositorio.obtener_por_id(medico_id) is None:
            raise RecursoNoEncontradoError("El médico no existe.")
        if self.cita_repositorio.medico_tiene_cita_activa(medico_id, fecha_hora):
            raise HorarioNoDisponibleError(
                "El médico ya tiene una cita activa en ese horario."
            )

        cita = Cita(paciente_id, medico_id, fecha_hora)
        return self.cita_repositorio.guardar(cita)
