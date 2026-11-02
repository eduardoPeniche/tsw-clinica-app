"""Configuración común de las pruebas E2E.

La app debe estar corriendo (`docker compose up`). Las URLs se pueden
sobrescribir con las variables E2E_BASE_URL (frontend) y E2E_API_URL (API).
"""

import os
import subprocess
import uuid

import pytest

API_URL = os.environ.get("E2E_API_URL", "http://localhost:8000")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_BORRAR_CITAS = (
    "import sqlite3;c=sqlite3.connect('/data/clinica.db');"
    "c.execute(\"DELETE FROM citas WHERE paciente_id IN (SELECT id FROM pacientes WHERE nombre LIKE 'E2E %') "
    "OR medico_id IN (SELECT id FROM medicos WHERE nombre LIKE 'E2E %')\");c.commit()"
)


def borrar_citas_e2e():
    """La API no puede borrar citas y borrar un paciente/médico con citas da 500.
    Se eliminan las citas E2E directo en SQLite, dentro del contenedor del backend."""
    subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "python", "-c", _BORRAR_CITAS],
        cwd=RAIZ, check=True, capture_output=True,
    )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
        "locale": "es-MX",
        "timezone_id": "America/Merida",
    }


@pytest.fixture
def api(playwright):
    """Cliente HTTP contra la API del backend, para preparar y limpiar datos."""
    context = playwright.request.new_context(base_url=API_URL)
    yield context
    context.dispose()


@pytest.fixture
def nombre_unico():
    """Nombre irrepetible para no chocar con datos de otras corridas."""
    return f"E2E Paciente {uuid.uuid4().hex[:8]}"


@pytest.fixture
def limpiar_pacientes(api):
    """Borra por API los pacientes cuyo nombre empiece por 'E2E ' al terminar."""
    yield
    borrar_citas_e2e()
    for paciente in api.get("/pacientes").json():
        if paciente["nombre"].startswith("E2E "):
            api.delete(f"/pacientes/{paciente['id']}")


@pytest.fixture
def limpiar_medicos(api):
    """Borra por API los médicos cuyo nombre empiece por 'E2E ' al terminar."""
    yield
    borrar_citas_e2e()
    for medico in api.get("/medicos").json():
        if medico["nombre"].startswith("E2E "):
            api.delete(f"/medicos/{medico['id']}")


@pytest.fixture
def paciente_api(api, limpiar_pacientes, nombre_unico):
    """Paciente creado por API (se borra solo al terminar)."""
    r = api.post("/pacientes", data={"nombre": nombre_unico, "fecha_nacimiento": "1990-01-01", "contacto": "555-0000"})
    assert r.ok
    return r.json()


@pytest.fixture
def medico_api(api, limpiar_medicos):
    """Médico creado por API (se borra solo al terminar)."""
    r = api.post("/medicos", data={"nombre": f"E2E Medico {uuid.uuid4().hex[:8]}", "especialidad": "Pruebas"})
    assert r.ok
    return r.json()


@pytest.fixture(autouse=True)
def pausa_final(page):
    """Al terminar cada test espera E2E_PAUSA_FINAL ms (0 por defecto).

    Playwright corta el video en cuanto termina el test, y las aserciones finales
    pasan casi al instante: sin pausa, el video no alcanza a mostrar el resultado."""
    yield
    pausa = int(os.environ.get("E2E_PAUSA_FINAL", "0"))
    if pausa:
        page.wait_for_timeout(pausa)
