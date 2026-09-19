from datetime import date, datetime, time, timedelta
import unittest
from uuid import uuid4
from zoneinfo import ZoneInfo

from clinica_app.domain.entities import Cita
from clinica_app.domain.exceptions import ValidacionDominioError
from clinica_app.domain.policies import EstadoSlot, PoliticaAgenda


class PoliticaAgendaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.zona_horaria = ZoneInfo("America/Merida")
        self.politica = PoliticaAgenda(
            frozenset({0, 1, 2, 3, 4}),
            time(9, 0),
            time(17, 0),
            timedelta(minutes=30),
            self.zona_horaria,
        )

    def test_acepta_el_ultimo_slot_del_viernes(self) -> None:
        fecha_hora = self.politica.normalizar_y_validar(datetime(2026, 10, 2, 16, 30))

        self.assertEqual(fecha_hora.tzinfo, self.zona_horaria)
        self.assertEqual(fecha_hora.hour, 16)
        self.assertEqual(fecha_hora.minute, 30)

    def test_rechaza_una_cita_que_termina_despues_del_cierre(self) -> None:
        with self.assertRaisesRegex(ValidacionDominioError, "horario de atención"):
            self.politica.normalizar_y_validar(datetime(2026, 10, 2, 17, 0))

    def test_rechaza_un_slot_que_no_es_de_media_hora(self) -> None:
        with self.assertRaisesRegex(ValidacionDominioError, "cada 30 minutos"):
            self.politica.normalizar_y_validar(datetime(2026, 10, 1, 9, 15))

    def test_rechaza_citas_en_fin_de_semana(self) -> None:
        with self.assertRaisesRegex(ValidacionDominioError, "lunes a viernes"):
            self.politica.normalizar_y_validar(datetime(2026, 10, 3, 9, 0))

    def test_cita_historica_bloquea_los_slots_que_se_traslapan(self) -> None:
        cita = Cita(
            paciente_id=uuid4(),
            medico_id=uuid4(),
            fecha_hora=datetime(2026, 10, 1, 11, 1, tzinfo=self.zona_horaria),
        )

        disponibilidad = self.politica.disponibilidad_en_fecha(
            date(2026, 10, 1),
            [cita],
            ahora=datetime(2026, 9, 1, 8, 0, tzinfo=self.zona_horaria),
        )

        estados = {slot.inicio.strftime("%H:%M"): slot.estado for slot in disponibilidad.slots}
        self.assertEqual(estados["11:00"], EstadoSlot.OCUPADO)
        self.assertEqual(estados["11:30"], EstadoSlot.OCUPADO)

    def test_slots_que_ya_iniciaron_no_estan_disponibles(self) -> None:
        disponibilidad = self.politica.disponibilidad_en_fecha(
            date(2026, 10, 1),
            [],
            ahora=datetime(2026, 10, 1, 10, 15, tzinfo=self.zona_horaria),
        )

        estados = {slot.inicio.strftime("%H:%M"): slot.estado for slot in disponibilidad.slots}
        self.assertEqual(estados["10:00"], EstadoSlot.NO_DISPONIBLE)
        self.assertEqual(estados["10:30"], EstadoSlot.LIBRE)
        self.assertEqual(disponibilidad.slot_recomendado, time(10, 30))
