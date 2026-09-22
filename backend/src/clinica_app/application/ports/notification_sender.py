from typing import Protocol

from clinica_app.domain.entities import Cita, Medico, Paciente


class NotificationSender(Protocol):
    def send_appointment_created(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None: ...
