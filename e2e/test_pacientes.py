import pytest
from playwright.sync_api import Page, expect

from pages.pacientes_page import PacientesPage

pytestmark = pytest.mark.usefixtures("limpiar_pacientes")


def test_crear_paciente(page: Page, nombre_unico):
    pacientes = PacientesPage(page)
    pacientes.abrir()
    pacientes.crear(nombre_unico, "1990-05-20", "555-1234")

    expect(page.get_by_role("status")).to_contain_text("Paciente creado")
    expect(pacientes.fila(nombre_unico)).to_contain_text("1990-05-20")
    expect(pacientes.fila(nombre_unico)).to_contain_text("555-1234")


def test_editar_paciente(page: Page, api, nombre_unico):
    api.post("/pacientes", data={"nombre": nombre_unico, "fecha_nacimiento": "1985-01-01", "contacto": "a@b.mx"})
    nuevo = nombre_unico + " editado"

    pacientes = PacientesPage(page)
    pacientes.abrir()
    pacientes.editar(nombre_unico, nuevo)

    expect(page.get_by_role("status")).to_contain_text("Paciente actualizado")
    expect(pacientes.fila(nuevo)).to_be_visible()


def test_eliminar_paciente(page: Page, api, nombre_unico):
    api.post("/pacientes", data={"nombre": nombre_unico, "fecha_nacimiento": "1985-01-01", "contacto": "a@b.mx"})

    pacientes = PacientesPage(page)
    pacientes.abrir()
    pacientes.eliminar(nombre_unico)

    expect(page.get_by_role("status")).to_contain_text("Paciente eliminado")
    expect(pacientes.fila(nombre_unico)).to_have_count(0)


def test_nombre_obligatorio(page: Page):
    pacientes = PacientesPage(page)
    pacientes.abrir()
    pacientes.vista.get_by_role("button", name="Agregar").click()
    pacientes.dialogo.get_by_role("button", name="Guardar").click()

    # La validación HTML5 impide enviar; el diálogo sigue abierto.
    expect(pacientes.dialogo).to_be_visible()


def test_cancelar_eliminacion_conserva_paciente(page: Page, nombre_unico):
    """Flujo grabado: crear un paciente y cancelar el cuadro de confirmación al eliminar."""
    pacientes = PacientesPage(page)
    pacientes.abrir()
    pacientes.crear(nombre_unico, "2026-11-02", "9999736473")
    expect(pacientes.fila(nombre_unico)).to_be_visible()

    pacientes.cancelar_eliminacion(nombre_unico)

    expect(pacientes.fila(nombre_unico)).to_be_visible()
    expect(page.get_by_role("status")).not_to_contain_text("Paciente eliminado")
