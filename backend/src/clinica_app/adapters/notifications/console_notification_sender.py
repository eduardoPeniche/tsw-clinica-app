import sys

from clinica_app.domain.entities import Cita, Medico, Paciente


class ConsoleNotificationSender:
    def send_appointment_created(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        self._print("Notificación de cita creada", cita, paciente, medico)

    def send_appointment_cancelled(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        self._print("Notificación de cita cancelada", cita, paciente, medico)

    def _print(
        self,
        titulo: str,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        print(
            f"{titulo}: "
            f"paciente={paciente.nombre}; "
            f"médico={medico.nombre}; "
            f"fecha_hora={cita.fecha_hora.isoformat()}; "
            f"estado={cita.estado.value}",
            file=sys.stderr,
        )
