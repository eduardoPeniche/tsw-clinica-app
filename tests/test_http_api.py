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
