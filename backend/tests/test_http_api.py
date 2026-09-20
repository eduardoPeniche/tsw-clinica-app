from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from clinica_app.adapters.http.dependencies import get_container
from clinica_app.container import build_container
from clinica_app.main import app


class HttpApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        container = build_container(Path(self.temporary_directory.name) / "api.db")
        app.dependency_overrides[get_container] = lambda: container
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.temporary_directory.cleanup()

    def test_crud_paciente(self) -> None:
        created = self.client.post("/pacientes", json={"nombre": "Ana López", "fecha_nacimiento": "1999-04-12", "contacto": "ana@example.com"})
        self.assertEqual(created.status_code, 201)
        paciente_id = created.json()["id"]
        self.assertEqual(self.client.get(f"/pacientes/{paciente_id}").status_code, 200)
        updated = self.client.put(f"/pacientes/{paciente_id}", json={"nombre": "Ana María López", "fecha_nacimiento": "1999-04-12", "contacto": "555-0101"})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f"/pacientes/{paciente_id}").status_code, 204)

    def test_conflicto_de_horario_devuelve_409(self) -> None:
        paciente = self.client.post("/pacientes", json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"}).json()
        otro = self.client.post("/pacientes", json={"nombre": "Luis", "fecha_nacimiento": "1998-04-12", "contacto": "l@x.com"}).json()
        medico = self.client.post("/medicos", json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"}).json()
        payload = {"paciente_id": paciente["id"], "medico_id": medico["id"], "fecha_hora": "2026-10-01T09:00:00"}
        cita = self.client.post("/citas", json=payload)
        self.assertEqual(cita.status_code, 201)
        payload["paciente_id"] = otro["id"]
        self.assertEqual(self.client.post("/citas", json=payload).status_code, 409)
        self.assertEqual(self.client.patch(f"/citas/{cita.json()['id']}/cancelacion").status_code, 200)
        self.assertEqual(self.client.post("/citas", json=payload).status_code, 201)

    def test_horario_fuera_de_atencion_devuelve_422(self) -> None:
        paciente = self.client.post(
            "/pacientes",
            json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"},
        ).json()
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()

        response = self.client.post(
            "/citas",
            json={
                "paciente_id": paciente["id"],
                "medico_id": medico["id"],
                "fecha_hora": "2026-10-03T09:00:00",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("lunes a viernes", response.json()["detail"])

    def test_lista_citas_de_un_medico_en_una_fecha(self) -> None:
        paciente = self.client.post(
            "/pacientes",
            json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"},
        ).json()
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()
        for fecha_hora in ("2026-10-01T09:00:00", "2026-10-02T09:00:00"):
            self.assertEqual(
                self.client.post(
                    "/citas",
                    json={
                        "paciente_id": paciente["id"],
                        "medico_id": medico["id"],
                        "fecha_hora": fecha_hora,
                    },
                ).status_code,
                201,
            )

        response = self.client.get(f"/medicos/{medico['id']}/citas?fecha=2026-10-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertTrue(response.json()[0]["fecha_hora"].startswith("2026-10-01"))

    def test_lista_citas_de_un_medico_en_un_rango(self) -> None:
        paciente = self.client.post(
            "/pacientes",
            json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"},
        ).json()
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()
        for fecha_hora in ("2026-10-01T09:00:00", "2026-10-02T09:00:00"):
            self.client.post(
                "/citas",
                json={
                    "paciente_id": paciente["id"],
                    "medico_id": medico["id"],
                    "fecha_hora": fecha_hora,
                },
            )

        response = self.client.get(
            f"/medicos/{medico['id']}/citas/rango?desde=2026-10-01&hasta=2026-10-02"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_disponibilidad_del_medico_devuelve_slots_con_estado(self) -> None:
        paciente = self.client.post(
            "/pacientes",
            json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"},
        ).json()
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()
        self.client.post(
            "/citas",
            json={
                "paciente_id": paciente["id"],
                "medico_id": medico["id"],
                "fecha_hora": "2026-10-01T09:00:00",
            },
        )

        response = self.client.get(f"/medicos/{medico['id']}/disponibilidad?fecha=2026-10-01")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["zona_horaria"], "America/Merida")
        self.assertEqual(payload["slots"][0], {"inicio": "09:00", "fin": "09:30", "estado": "ocupado"})
        self.assertEqual(payload["slots"][1]["estado"], "libre")

    def test_disponibilidad_por_rango_devuelve_slots_de_cada_dia(self) -> None:
        paciente = self.client.post(
            "/pacientes",
            json={"nombre": "Ana", "fecha_nacimiento": "1999-04-12", "contacto": "a@x.com"},
        ).json()
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()
        self.client.post(
            "/citas",
            json={
                "paciente_id": paciente["id"],
                "medico_id": medico["id"],
                "fecha_hora": "2026-10-01T09:00:00",
            },
        )

        response = self.client.get(
            f"/medicos/{medico['id']}/disponibilidad/rango?desde=2026-10-01&hasta=2026-10-02"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["duracion_minutos"], 30)
        self.assertEqual([dia["fecha"] for dia in payload["dias"]], ["2026-10-01", "2026-10-02"])
        self.assertEqual(payload["dias"][0]["slots"][0]["estado"], "ocupado")
        self.assertEqual(payload["dias"][1]["slots"][0]["estado"], "libre")

    def test_disponibilidad_por_rango_rechaza_mas_de_31_dias(self) -> None:
        medico = self.client.post(
            "/medicos",
            json={"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
        ).json()

        response = self.client.get(
            f"/medicos/{medico['id']}/disponibilidad/rango?desde=2026-10-01&hasta=2026-11-01"
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("31 días", response.json()["detail"])
