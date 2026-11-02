import re

from playwright.sync_api import Page, expect


def test_carga_inicial_muestra_calendario(page: Page):
    page.goto("/")
    expect(page).to_have_title(re.compile("Clínica"))
    expect(page.get_by_role("heading", name="Calendario", level=1)).to_be_visible()


def test_navegar_entre_vistas(page: Page):
    page.goto("/")
    page.get_by_role("button", name="Pacientes").click()
    expect(page.get_by_role("heading", name="Pacientes")).to_be_visible()
    page.get_by_role("button", name="Médicos").click()
    expect(page.get_by_role("heading", name="Médicos")).to_be_visible()
    page.get_by_role("button", name="Calendario").click()
    expect(page.get_by_role("heading", name="Calendario", level=1)).to_be_visible()
