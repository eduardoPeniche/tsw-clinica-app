from playwright.sync_api import Page, expect


class MedicosPage:
    def __init__(self, page: Page):
        self.page = page
        self.vista = page.get_by_role("region", name="Médicos")
        self.dialogo = page.get_by_role("dialog")

    def abrir(self):
        self.page.goto("/")
        self.page.get_by_role("button", name="Médicos").click()
        expect(self.vista).to_be_visible()
        # Hidratación de React (client:visible): al terminar de cargar, ya es interactivo.
        expect(self.vista.get_by_text("Cargando médicos")).to_have_count(0)

    def fila(self, nombre: str):
        return self.vista.get_by_role("row").filter(has_text=nombre)

    def crear(self, nombre: str, especialidad: str):
        self.vista.get_by_role("button", name="Agregar").click()
        self.dialogo.get_by_label("Nombre").fill(nombre)
        self.dialogo.get_by_label("Especialidad").fill(especialidad)
        self.dialogo.get_by_role("button", name="Guardar").click()

    def editar(self, nombre: str, nuevo_nombre: str):
        self.fila(nombre).get_by_role("button", name="Editar").click()
        self.dialogo.get_by_label("Nombre").fill(nuevo_nombre)
        self.dialogo.get_by_role("button", name="Guardar").click()

    def eliminar(self, nombre: str):
        self.page.once("dialog", lambda d: d.accept())  # confirm() nativo
        self.fila(nombre).get_by_role("button", name="Eliminar").click()
