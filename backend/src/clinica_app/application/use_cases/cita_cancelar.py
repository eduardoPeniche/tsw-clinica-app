from uuid import UUID

from clinica_app.application.exceptions import RecursoNoEncontradoError
from clinica_app.application.ports import (
    CitaRepository,
    MedicoRepository,
    NotificationSender,
    PacienteRepository,
)
from clinica_app.domain.entities import Cita, EstadoCita


class CancelarCita:
    def __init__(
        self,
        cita_repositorio: CitaRepository,
        paciente_repositorio: PacienteRepository,
        medico_repositorio: MedicoRepository,
        notification_sender: NotificationSender,
    ) -> None:
        self.cita_repositorio = cita_repositorio
        self.paciente_repositorio = paciente_repositorio
        self.medico_repositorio = medico_repositorio
        self.notification_sender = notification_sender

    def ejecutar(self, cita_id: UUID) -> Cita:
        cita = self.cita_repositorio.obtener_por_id(cita_id)
        if cita is None:
            raise RecursoNoEncontradoError("La cita no existe.")
        # La cancelación es idempotente: repetirla no vuelve a notificar.
        if cita.estado == EstadoCita.CANCELADA:
            return cita

        cita.cancelar()
        cita = self.cita_repositorio.actualizar(cita)
        paciente = self.paciente_repositorio.obtener_por_id(cita.paciente_id)
        medico = self.medico_repositorio.obtener_por_id(cita.medico_id)
        if paciente is not None and medico is not None:
            self.notification_sender.send_appointment_cancelled(cita, paciente, medico)
        return cita
