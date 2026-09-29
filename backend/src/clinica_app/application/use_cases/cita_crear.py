from datetime import datetime
from uuid import UUID

from clinica_app.application.exceptions import (
    HorarioNoDisponibleError,
    RecursoNoEncontradoError,
)
from clinica_app.application.ports import (
    CitaRepository,
    MedicoRepository,
    NotificationSender,
    PacienteRepository,
)
from clinica_app.domain.entities import Cita
from clinica_app.domain.policies import PoliticaAgenda


class CrearCita:
    def __init__(
        self,
        cita_repositorio: CitaRepository,
        paciente_repositorio: PacienteRepository,
        medico_repositorio: MedicoRepository,
        politica_agenda: PoliticaAgenda,
        notification_sender: NotificationSender,
    ) -> None:
        self.cita_repositorio = cita_repositorio
        self.paciente_repositorio = paciente_repositorio
        self.medico_repositorio = medico_repositorio
        self.politica_agenda = politica_agenda
        self.notification_sender = notification_sender

    def ejecutar(
        self,
        paciente_id: UUID,
        medico_id: UUID,
        fecha_hora: datetime,
    ) -> Cita:
        paciente = self.paciente_repositorio.obtener_por_id(paciente_id)
        if paciente is None:
            raise RecursoNoEncontradoError("El paciente no existe.")
        medico = self.medico_repositorio.obtener_por_id(medico_id)
        if medico is None:
            raise RecursoNoEncontradoError("El médico no existe.")
        fecha_hora = self.politica_agenda.normalizar_y_validar(fecha_hora)
        if self.cita_repositorio.medico_tiene_cita_activa_en_intervalo(
            medico_id,
            fecha_hora,
            self.politica_agenda.fin_de_cita(fecha_hora),
        ):
            raise HorarioNoDisponibleError(
                "El médico ya tiene una cita activa en ese horario."
            )

        cita = Cita(paciente_id, medico_id, fecha_hora)
        cita = self.cita_repositorio.guardar(cita)
        self.notification_sender.send_appointment_created(cita, paciente, medico)
        return cita
