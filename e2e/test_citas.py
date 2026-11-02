import re

from playwright.sync_api import Page, expect

from pages.calendario_page import CalendarioPage

LIBRE = re.compile("^libre")
OCUPADO = re.compile("^ocupado")


def test_agendar_cita(page: Page, paciente_api, medico_api):
    calendario = CalendarioPage(page)
    calendario.abrir(medico_api)
    calendario.agendar_en_primer_hueco(paciente_api["nombre"])

    expect(page.get_by_role("status")).to_contain_text("Cita agendada")
    fila = calendario.fila_cita(paciente_api["nombre"])
    expect(fila).to_be_visible()
    expect(fila).to_contain_text("pendiente")
    calendario.mostrar_citas()


def test_cancelar_cita(page: Page, api, paciente_api, medico_api):
    calendario = CalendarioPage(page)
    calendario.abrir(medico_api)
    calendario.agendar_en_primer_hueco(paciente_api["nombre"])
    expect(calendario.fila_cita(paciente_api["nombre"])).to_be_visible()

    calendario.cancelar_cita(paciente_api["nombre"])

    expect(page.get_by_role("status")).to_contain_text("Cita cancelada")
    expect(calendario.fila_cita(paciente_api["nombre"])).to_contain_text("cancelada")
    calendario.mostrar_citas()


def test_hueco_ocupado_deja_de_estar_libre(page: Page, paciente_api, medico_api):
    calendario = CalendarioPage(page)
    calendario.abrir(medico_api)
    libres = page.get_by_role("button", name=LIBRE)
    expect(libres.first).to_be_visible()
    libres_antes = libres.count()

    calendario.agendar_en_primer_hueco(paciente_api["nombre"])

    ocupado = page.get_by_role("button", name=OCUPADO)
    expect(ocupado).to_have_count(1)
    expect(ocupado).to_be_disabled()
    expect(ocupado).to_have_text(paciente_api["nombre"])
    expect(libres).to_have_count(libres_antes - 1)
