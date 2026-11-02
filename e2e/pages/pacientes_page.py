from playwright.sync_api import Page, expect


class PacientesPage:
    def __init__(self, page: Page):
        self.page = page
        self.vista = page.get_by_role("region", name="Pacientes")
        self.dialogo = page.get_by_role("dialog")

    def abrir(self):
        self.page.goto("/")
        self.page.get_by_role("button", name="Pacientes").click()
        expect(self.vista).to_be_visible()
        # Hidratación de React (client:visible): al terminar de cargar, ya es interactivo.
        expect(self.vista.get_by_text("Cargando pacientes")).to_have_count(0)

    def fila(self, nombre: str):
        return self.vista.get_by_role("row").filter(has_text=nombre)

    def crear(self, nombre: str, nacimiento: str, contacto: str):
        self.vista.get_by_role("button", name="Agregar").click()
        self._llenar(nombre, nacimiento, contacto)

    def editar(self, nombre: str, nuevo_nombre: str):
        self.fila(nombre).get_by_role("button", name="Editar").click()
        self.dialogo.get_by_label("Nombre completo").fill(nuevo_nombre)
        self.dialogo.get_by_role("button", name="Guardar").click()

    def eliminar(self, nombre: str):
        self.page.once("dialog", lambda d: d.accept())  # confirm() nativo
        self.fila(nombre).get_by_role("button", name="Eliminar").click()

    def cancelar_eliminacion(self, nombre: str):
        self.page.once("dialog", lambda d: d.dismiss())  # el usuario pulsa "Cancelar"
        self.fila(nombre).get_by_role("button", name="Eliminar").click()

    def _llenar(self, nombre: str, nacimiento: str, contacto: str):
        self.dialogo.get_by_label("Nombre completo").fill(nombre)
        self.dialogo.get_by_label("Fecha de nacimiento").fill(nacimiento)
        self.dialogo.get_by_label("Contacto").fill(contacto)
        self.dialogo.get_by_role("button", name="Guardar").click()
