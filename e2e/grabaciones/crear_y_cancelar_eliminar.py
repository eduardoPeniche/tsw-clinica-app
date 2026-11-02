import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("http://localhost:4321/")
    page.get_by_role("button", name="Pacientes").click()
    page.get_by_role("button", name="Agregar").click()
    page.get_by_role("textbox", name="Nombre completo").click()
    page.get_by_role("textbox", name="Nombre completo").fill("prueba")
    page.get_by_role("textbox", name="Fecha de nacimiento").fill("2026-11-02")
    page.get_by_role("textbox", name="Contacto").click()
    page.get_by_role("textbox", name="Contacto").fill("9999736473")
    page.get_by_role("button", name="Guardar").click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Eliminar").nth(2).click()
