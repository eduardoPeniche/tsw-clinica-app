# Guía de Playwright (Python) para pruebas E2E

Guía reutilizable para agregar pruebas end-to-end con Playwright a cualquier proyecto web. Documentación oficial: https://playwright.dev/python/docs/intro

## 1. ¿Qué es y cuándo usarlo?

Playwright controla un navegador real (Chromium, Firefox, WebKit) como lo haría un usuario: abre páginas, hace clic, escribe y verifica lo que se ve. Sirve para probar **flujos completos** (frontend + backend + base de datos), no funciones aisladas.

Requisito: la aplicación debe estar **corriendo** (local, Docker o un entorno de staging) antes de ejecutar las pruebas.

## 2. Instalación

Desde la raíz del proyecto (o en una carpeta `e2e/`):

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pytest-playwright
playwright install                 # descarga los navegadores
```

Opcional, solo un navegador: `playwright install chromium`.

Guarda las dependencias:

```bash
pip freeze | grep -i -E "playwright|pytest" > requirements-e2e.txt
```

> Añade `.venv/` a `.gitignore`. No subas el entorno virtual al repositorio.

## 3. Estructura recomendada

```
proyecto/
├── e2e/
│   ├── conftest.py          # configuración común (URL base, fixtures)
│   ├── test_home.py
│   ├── test_login.py
│   └── pages/               # (opcional) Page Objects
├── pytest.ini
└── requirements-e2e.txt
```

`pytest.ini`:

```ini
[pytest]
testpaths = e2e
addopts = --base-url=http://localhost:8000
```

Con `--base-url` puedes usar rutas relativas: `page.goto("/view")`.

## 4. Grabar una prueba con codegen

La forma más rápida de empezar. Abre un navegador y una ventana que genera el código mientras navegas:

```bash
playwright codegen http://localhost:8000
playwright codegen --target python-pytest -o e2e/test_flujo.py http://localhost:8000
```

Resultado típico:

```python
import re
from playwright.sync_api import Page, expect

def test_example(page: Page) -> None:
    page.goto("http://localhost:8000/view")
```

**Importante:** lo grabado es solo un borrador. Hay que renombrar el test, quitar imports sin usar y **añadir aserciones** (`expect`). Un test sin `expect` solo comprueba que la página no explota.

## 5. Escribir un test

```python
from playwright.sync_api import Page, expect

def test_suma_de_matrices(page: Page) -> None:
    page.goto("/")

    page.get_by_label("Matriz A").fill("1,2;3,4")
    page.get_by_label("Matriz B").fill("5,6;7,8")
    page.get_by_role("button", name="Sumar").click()

    expect(page.locator("#resultado")).to_contain_text("6")
    expect(page).to_have_title(re.compile("Calculadora"))
```

### Localizadores (de más a menos recomendado)

| Localizador | Ejemplo |
|---|---|
| Por rol | `page.get_by_role("button", name="Enviar")` |
| Por etiqueta | `page.get_by_label("Correo")` |
| Por texto | `page.get_by_text("Bienvenido")` |
| Por placeholder | `page.get_by_placeholder("Buscar...")` |
| Por test id | `page.get_by_test_id("btn-guardar")` (atributo `data-testid`) |
| CSS / XPath | `page.locator("#resultado")` — último recurso |

### Acciones habituales

```python
page.goto("/ruta")
locator.click()
locator.fill("texto")            # reemplaza el contenido
locator.press("Enter")
locator.select_option("opcion")
locator.check() / uncheck()
locator.set_input_files("archivo.pdf")
page.screenshot(path="captura.png", full_page=True)
```

### Aserciones (`expect`, con espera automática)

```python
expect(locator).to_be_visible()
expect(locator).to_have_text("exacto")
expect(locator).to_contain_text("parcial")
expect(locator).to_have_value("valor de input")
expect(locator).to_have_count(3)
expect(page).to_have_url("http://localhost:8000/view")
```

`expect` reintenta hasta ~5 s, así que normalmente **no necesitas `sleep`**. Evita `time.sleep()`.

## 6. Ejecutar las pruebas

```bash
pytest                              # headless (sin ventana), todos los tests
pytest --headed                     # con ventana visible
pytest e2e/test_login.py            # un archivo
pytest -k "suma"                    # tests cuyo nombre contenga "suma"
pytest --browser firefox            # otro navegador
pytest --browser chromium --browser firefox --browser webkit
pytest --slowmo 500                 # ralentiza (ms) para ver qué pasa
pytest --screenshot=only-on-failure # captura si falla
pytest --video=retain-on-failure    # video si falla
pytest --tracing=retain-on-failure  # traza si falla
```

Los artefactos se guardan en `test-results/`.

## 7. Depurar

- **Inspector:** `PWDEBUG=1 pytest -s e2e/test_login.py` (paso a paso).
- **Pausa manual:** inserta `page.pause()` en el test.
- **Trace Viewer:** tras una falla con `--tracing=retain-on-failure`:
  ```bash
  playwright show-trace test-results/<carpeta>/trace.zip
  ```
- **Generar localizadores:** en codegen, usa el botón "Pick locator".

## 8. Buenas prácticas

1. **Cada test es independiente**: no dependas del orden ni del estado de otro test. `pytest-playwright` ya da un contexto de navegador limpio por test.
2. **Prefiere `get_by_role` / `get_by_label`** antes que CSS; son más estables y mejoran la accesibilidad.
3. **Siempre aserta** el resultado esperado.
4. **No pruebes sitios de terceros**; usa tu propia app o un entorno de pruebas.
5. **No pongas credenciales en el código**; usa variables de entorno (`os.environ["E2E_PASSWORD"]`).
6. Usa **datos de prueba** controlados (base de datos de test o semillas).
7. Cubre pocos flujos **críticos** end-to-end; deja la lógica fina para pruebas unitarias.

## 9. Fixtures y configuración común (`conftest.py`)

```python
import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}, "locale": "es-ES"}

@pytest.fixture
def pagina_inicio(page):
    page.goto("/")
    return page
```

### Reutilizar un inicio de sesión

```python
# guarda el estado una vez
context.storage_state(path="auth.json")

# reutilízalo
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "storage_state": "auth.json"}
```

## 10. Page Object Model (opcional)

Agrupa localizadores y acciones de una página para no repetirlos:

```python
class CalculadoraPage:
    def __init__(self, page):
        self.page = page
        self.resultado = page.locator("#resultado")

    def abrir(self):
        self.page.goto("/")

    def sumar(self, a, b):
        self.page.get_by_label("Matriz A").fill(a)
        self.page.get_by_label("Matriz B").fill(b)
        self.page.get_by_role("button", name="Sumar").click()
```

```python
def test_suma(page):
    calc = CalculadoraPage(page)
    calc.abrir()
    calc.sumar("1,2;3,4", "5,6;7,8")
    expect(calc.resultado).to_contain_text("6")
```

## 11. Probar la API (sin navegador)

```python
def test_api(playwright):
    request = playwright.request.new_context(base_url="http://localhost:8000")
    r = request.get("/health")
    assert r.ok
    assert r.json()["status"] == "ok"
```

## 12. Integración con Docker y CI

Levantar la app antes de las pruebas:

```bash
docker compose up -d
pytest
docker compose down
```

GitHub Actions (ejemplo mínimo):

```yaml
name: e2e
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements-e2e.txt
      - run: playwright install --with-deps chromium
      - run: docker compose up -d
      - run: pytest --tracing=retain-on-failure
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: test-results, path: test-results/ }
```

## 13. Problemas frecuentes

| Síntoma | Causa / solución |
|---|---|
| `net::ERR_CONNECTION_REFUSED` | La app no está levantada o el puerto es otro. |
| `Executable doesn't exist` | Falta `playwright install`. |
| Timeout esperando un elemento | Localizador incorrecto o la página tarda; revisa con codegen / trace. |
| Test pasa a veces y falla otras (flaky) | Hay `sleep` o dependencia entre tests; usa `expect` y aísla datos. |
| Strict mode violation | El localizador coincide con varios elementos; hazlo más específico o usa `.first`. |

## 14. Lista rápida de comandos

```bash
pip install pytest-playwright && playwright install
playwright codegen <url>
pytest --headed
pytest --tracing=retain-on-failure
playwright show-trace <trace.zip>
```

## 15. Recursos

- Introducción: https://playwright.dev/python/docs/intro
- Localizadores: https://playwright.dev/python/docs/locators
- Aserciones: https://playwright.dev/python/docs/test-assertions
- Codegen: https://playwright.dev/python/docs/codegen
- Trace Viewer: https://playwright.dev/python/docs/trace-viewer
- CI: https://playwright.dev/python/docs/ci
