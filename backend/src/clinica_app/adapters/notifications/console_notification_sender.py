import sys

from clinica_app.domain.entities import Cita, Medico, Paciente


class ConsoleNotificationSender:
    def send_appointment_created(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        print(
            "Notificación de cita creada: "
            f"paciente={paciente.nombre}; "
            f"médico={medico.nombre}; "
            f"fecha_hora={cita.fecha_hora.isoformat()}; "
            f"estado={cita.estado.value}",
            file=sys.stderr,
        )
