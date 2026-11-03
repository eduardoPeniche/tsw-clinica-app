import json
import sys
from urllib.request import Request, urlopen

from clinica_app.domain.entities import Cita, Medico, Paciente


def _evento(
    nombre: str,
    cita: Cita,
    paciente: Paciente,
    medico: Medico,
) -> dict[str, object]:
    return {
        "evento": nombre,
        "cita": {
            "id": str(cita.id),
            "fecha_hora": cita.fecha_hora.isoformat(),
            "estado": cita.estado.value,
        },
        "paciente": {
            "id": str(paciente.id),
            "nombre": paciente.nombre,
            "contacto": paciente.contacto,
        },
        "medico": {
            "id": str(medico.id),
            "nombre": medico.nombre,
            "especialidad": medico.especialidad,
        },
    }


class WebhookNotificationSender:
    """Envía los eventos de citas como JSON a un webhook, por ejemplo de n8n.

    Un fallo del webhook no debe impedir crear o cancelar la cita: se informa
    en `stderr` y la operación continúa.
    """

    def __init__(
        self,
        url: str,
        token: str | None = None,
        timeout_seconds: float = 5.0,
    ) -> None:
        self.url = url
        self.token = token
        self.timeout_seconds = timeout_seconds

    def send_appointment_created(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        self._send(_evento("cita_creada", cita, paciente, medico))

    def send_appointment_cancelled(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        self._send(_evento("cita_cancelada", cita, paciente, medico))

    def _send(self, payload: dict[str, object]) -> None:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["X-Clinica-Token"] = self.token
        request = Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds):
                pass
        except OSError as error:
            print(
                f"No se pudo enviar el evento {payload['evento']} al webhook: {error}",
                file=sys.stderr,
            )
