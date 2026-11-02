import uuid

import pytest
from playwright.sync_api import Page, expect

from pages.medicos_page import MedicosPage

pytestmark = pytest.mark.usefixtures("limpiar_medicos")


@pytest.fixture
def nombre_medico():
    return f"E2E Medico {uuid.uuid4().hex[:8]}"


def test_crear_medico(page: Page, nombre_medico):
    medicos = MedicosPage(page)
    medicos.abrir()
    medicos.crear(nombre_medico, "Cardiología")

    expect(page.get_by_role("status")).to_contain_text("Médico creado")
    expect(medicos.fila(nombre_medico)).to_contain_text("Cardiología")


def test_editar_medico(page: Page, api, nombre_medico):
    api.post("/medicos", data={"nombre": nombre_medico, "especialidad": "Pediatría"})
    nuevo = nombre_medico + " editado"

    medicos = MedicosPage(page)
    medicos.abrir()
    medicos.editar(nombre_medico, nuevo)

    expect(page.get_by_role("status")).to_contain_text("Médico actualizado")
    expect(medicos.fila(nuevo)).to_be_visible()


def test_eliminar_medico(page: Page, api, nombre_medico):
    api.post("/medicos", data={"nombre": nombre_medico, "especialidad": "Pediatría"})

    medicos = MedicosPage(page)
    medicos.abrir()
    medicos.eliminar(nombre_medico)

    expect(page.get_by_role("status")).to_contain_text("Médico eliminado")
    expect(medicos.fila(nombre_medico)).to_have_count(0)


def test_campos_obligatorios(page: Page):
    medicos = MedicosPage(page)
    medicos.abrir()
    medicos.vista.get_by_role("button", name="Agregar").click()
    medicos.dialogo.get_by_role("button", name="Guardar").click()

    # La validación HTML5 impide enviar; el diálogo sigue abierto.
    expect(medicos.dialogo).to_be_visible()
