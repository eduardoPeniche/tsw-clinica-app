import contextlib
import io
import json
import os
import threading
import unittest
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar
from unittest import mock
from zoneinfo import ZoneInfo

from clinica_app.adapters.notifications import (
    ConsoleNotificationSender,
    WebhookNotificationSender,
)
from clinica_app.container import notification_sender_from_environment
from clinica_app.domain.entities import Cita, Medico, Paciente


class _RecordingHandler(BaseHTTPRequestHandler):
    requests: ClassVar[list[tuple[dict[str, str], dict[str, object]]]] = []

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.requests.append((dict(self.headers), json.loads(body)))
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


class WebhookNotificationSenderTests(unittest.TestCase):
    def setUp(self) -> None:
        _RecordingHandler.requests = []
        self.server = HTTPServer(("127.0.0.1", 0), _RecordingHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/webhook"
        self.paciente = Paciente("Ana López", date(1999, 4, 12), "ana@example.com")
        self.medico = Medico("Dr. Ruiz", "Cardiología")
        self.cita = Cita(
            self.paciente.id,
            self.medico.id,
            datetime(2026, 11, 4, 10, 0, tzinfo=ZoneInfo("America/Merida")),
        )

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def test_envia_cita_creada_como_json(self) -> None:
        sender = WebhookNotificationSender(self.url, token="secreto")

        sender.send_appointment_created(self.cita, self.paciente, self.medico)

        headers, payload = _RecordingHandler.requests[0]
        self.assertEqual(headers["X-Clinica-Token"], "secreto")
        self.assertEqual(payload["evento"], "cita_creada")
        self.assertEqual(payload["cita"]["id"], str(self.cita.id))
        self.assertEqual(payload["cita"]["fecha_hora"], "2026-11-04T10:00:00-06:00")
        self.assertEqual(payload["cita"]["estado"], "pendiente")
        self.assertEqual(payload["paciente"]["contacto"], "ana@example.com")
        self.assertEqual(payload["medico"]["especialidad"], "Cardiología")

    def test_envia_cita_cancelada(self) -> None:
        self.cita.cancelar()

        WebhookNotificationSender(self.url).send_appointment_cancelled(
            self.cita, self.paciente, self.medico
        )

        _, payload = _RecordingHandler.requests[0]
        self.assertEqual(payload["evento"], "cita_cancelada")
        self.assertEqual(payload["cita"]["estado"], "cancelada")
        self.assertEqual(payload["paciente"]["nombre"], "Ana López")

    def test_omite_token_si_no_esta_configurado(self) -> None:
        WebhookNotificationSender(self.url).send_appointment_created(
            self.cita, self.paciente, self.medico
        )

        headers, _ = _RecordingHandler.requests[0]
        self.assertNotIn("X-Clinica-Token", headers)

    def test_fallo_del_webhook_no_interrumpe_la_operacion(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        sender = WebhookNotificationSender(self.url, timeout_seconds=1)
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            sender.send_appointment_created(self.cita, self.paciente, self.medico)

        self.assertIn("No se pudo enviar el evento cita_creada", stderr.getvalue())

    def test_container_usa_webhook_solo_si_hay_url(self) -> None:
        with mock.patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_URL": ""}):
            self.assertIsInstance(
                notification_sender_from_environment(), ConsoleNotificationSender
            )
        with mock.patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_URL": self.url}):
            self.assertIsInstance(
                notification_sender_from_environment(), WebhookNotificationSender
            )
