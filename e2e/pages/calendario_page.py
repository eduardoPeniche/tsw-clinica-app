import re

from playwright.sync_api import Page, expect


class CalendarioPage:
    def __init__(self, page: Page):
        self.page = page
        self.selector_medico = page.get_by_label("Médico a visualizar")
        self.dialogo_cita = page.get_by_role("dialog", name="Agendar consulta")
        self.tabla_citas = page.locator("#citas-body")

    def abrir(self, medico: dict):
        self.page.goto("/")
        # select_option espera a que la opción exista (los médicos se cargan por API).
        self.selector_medico.select_option(label=f"{medico['nombre']} · {medico['especialidad']}")
        self.page.get_by_role("button", name="Día", exact=True).click()

    def primer_hueco_libre(self):
        return self.page.get_by_role("button", name=re.compile("^libre")).first

    def agendar_en_primer_hueco(self, nombre_paciente: str):
        self.primer_hueco_libre().click()
        expect(self.dialogo_cita).to_be_visible()
        self.dialogo_cita.get_by_label("Paciente").select_option(label=nombre_paciente)
        self.dialogo_cita.get_by_role("button", name="Agendar cita").click()

    def fila_cita(self, nombre_paciente: str):
        return self.tabla_citas.get_by_role("row").filter(has_text=nombre_paciente)

    def cancelar_cita(self, nombre_paciente: str):
        self.page.once("dialog", lambda d: d.accept())  # confirm() nativo
        self.fila_cita(nombre_paciente).get_by_role("button", name="Cancelar").click()

    def mostrar_citas(self):
        """Lleva la tabla de citas a la vista (queda debajo del calendario) para que se vea en el video."""
        self.tabla_citas.scroll_into_view_if_needed()
