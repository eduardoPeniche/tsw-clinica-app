from datetime import date, datetime, time, timedelta
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from clinica_app.adapters.persistence.sqlite import SQLiteDatabase
from clinica_app.adapters.persistence.sqlite.cita_repository import SQLiteCitaRepository
from clinica_app.adapters.persistence.sqlite.medico_repository import SQLiteMedicoRepository
from clinica_app.adapters.persistence.sqlite.paciente_repository import (
    SQLitePacienteRepository,
)
from clinica_app.application.exceptions import HorarioNoDisponibleError
from clinica_app.domain.entities import Cita, EstadoCita, Medico, Paciente
from clinica_app.application.use_cases import (
    CancelarCita,
    CrearCita,
    CrearMedico,
    CrearPaciente,
)
from clinica_app.domain.policies import PoliticaAgenda


class RecordingNotificationSender:
    def __init__(self) -> None:
        self.appointments: list[tuple[Cita, Paciente, Medico]] = []

    def send_appointment_created(
        self,
        cita: Cita,
        paciente: Paciente,
        medico: Medico,
    ) -> None:
        self.appointments.append((cita, paciente, medico))


class SQLiteIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database = SQLiteDatabase(Path(self.temporary_directory.name) / "clinica.db")
        database.initialize()
        self.pacientes = SQLitePacienteRepository(database)
        self.medicos = SQLiteMedicoRepository(database)
        self.citas = SQLiteCitaRepository(database)
        self.notification_sender = RecordingNotificationSender()
        self.politica_agenda = PoliticaAgenda(
            frozenset({0, 1, 2, 3, 4}),
            time(9, 0),
            time(17, 0),
            timedelta(minutes=30),
            ZoneInfo("America/Merida"),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_crear_y_consultar_paciente(self) -> None:
        paciente = CrearPaciente(self.pacientes).ejecutar(
            "Ana López", date(1999, 4, 12), "ana@example.com"
        )

        encontrado = self.pacientes.obtener_por_id(paciente.id)

        self.assertEqual(encontrado, paciente)
        self.assertEqual(self.pacientes.listar(), [paciente])

    def test_rechaza_cita_activa_en_el_mismo_horario(self) -> None:
        paciente = CrearPaciente(self.pacientes).ejecutar(
            "Ana López", date(1999, 4, 12), "ana@example.com"
        )
        segundo_paciente = CrearPaciente(self.pacientes).ejecutar(
            "Luis Pérez", date(1995, 8, 20), "luis@example.com"
        )
        medico = CrearMedico(self.medicos).ejecutar("Dr. Ruiz", "Cardiología")
        crear_cita = CrearCita(
            self.citas,
            self.pacientes,
            self.medicos,
            self.politica_agenda,
            self.notification_sender,
        )
        horario = datetime(2026, 10, 1, 9, 0)

        cita = crear_cita.ejecutar(paciente.id, medico.id, horario)

        with self.assertRaises(HorarioNoDisponibleError):
            crear_cita.ejecutar(segundo_paciente.id, medico.id, horario)

        self.assertTrue(
            self.citas.medico_tiene_cita_activa_en_intervalo(
                medico.id,
                cita.fecha_hora,
                self.politica_agenda.fin_de_cita(cita.fecha_hora),
            )
        )
        self.assertEqual(cita.estado, EstadoCita.PENDIENTE)

    def test_cancelar_cita_libera_el_horario_y_es_idempotente(self) -> None:
        paciente = CrearPaciente(self.pacientes).ejecutar(
            "Ana López", date(1999, 4, 12), "ana@example.com"
        )
        medico = CrearMedico(self.medicos).ejecutar("Dr. Ruiz", "Cardiología")
        horario = datetime(2026, 10, 1, 9, 0)
        cita = CrearCita(
            self.citas,
            self.pacientes,
            self.medicos,
            self.politica_agenda,
            self.notification_sender,
        ).ejecutar(
            paciente.id, medico.id, horario
        )
        cancelar = CancelarCita(self.citas)

        cancelar.ejecutar(cita.id)
        cita_cancelada = cancelar.ejecutar(cita.id)

        self.assertEqual(cita_cancelada.estado, EstadoCita.CANCELADA)
        self.assertFalse(
            self.citas.medico_tiene_cita_activa_en_intervalo(
                medico.id,
                cita.fecha_hora,
                self.politica_agenda.fin_de_cita(cita.fecha_hora),
            )
        )

    def test_cita_historica_fuera_de_slot_bloquea_intervalos_superpuestos(self) -> None:
        paciente = CrearPaciente(self.pacientes).ejecutar(
            "Ana López", date(1999, 4, 12), "ana@example.com"
        )
        medico = CrearMedico(self.medicos).ejecutar("Dr. Ruiz", "Cardiología")
        cita_historica = Cita(
            paciente.id,
            medico.id,
            datetime(2026, 10, 1, 11, 1, tzinfo=ZoneInfo("America/Merida")),
        )
        self.citas.guardar(cita_historica)
        crear_cita = CrearCita(
            self.citas,
            self.pacientes,
            self.medicos,
            self.politica_agenda,
            self.notification_sender,
        )

        with self.assertRaises(HorarioNoDisponibleError):
            crear_cita.ejecutar(paciente.id, medico.id, datetime(2026, 10, 1, 11, 0))
        with self.assertRaises(HorarioNoDisponibleError):
            crear_cita.ejecutar(paciente.id, medico.id, datetime(2026, 10, 1, 11, 30))

    def test_notifies_after_persisting_an_appointment(self) -> None:
        paciente = CrearPaciente(self.pacientes).ejecutar(
            "Ana López", date(1999, 4, 12), "ana@example.com"
        )
        medico = CrearMedico(self.medicos).ejecutar("Dr. Ruiz", "Cardiología")
        cita = CrearCita(
            self.citas,
            self.pacientes,
            self.medicos,
            self.politica_agenda,
            self.notification_sender,
        ).ejecutar(paciente.id, medico.id, datetime(2026, 10, 1, 9, 0))

        self.assertEqual(self.notification_sender.appointments, [(cita, paciente, medico)])
