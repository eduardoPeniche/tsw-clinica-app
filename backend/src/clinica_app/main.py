from fastapi import FastAPI

from clinica_app.adapters.http.error_handlers import register_error_handlers
from clinica_app.adapters.http.routes import citas, medicos, pacientes

app = FastAPI(title="Sistema de gestión de citas médicas")
register_error_handlers(app)
app.include_router(pacientes.router)
app.include_router(medicos.router)
app.include_router(citas.router)
