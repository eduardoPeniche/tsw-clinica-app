from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from clinica_app.application.exceptions import (
    HorarioNoDisponibleError,
    RecursoNoEncontradoError,
)
from clinica_app.domain.exceptions import ValidacionDominioError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RecursoNoEncontradoError)
    def recurso_no_encontrado(
        _: Request, error: RecursoNoEncontradoError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(HorarioNoDisponibleError)
    def horario_no_disponible(
        _: Request, error: HorarioNoDisponibleError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(ValidacionDominioError)
    def validacion_dominio(_: Request, error: ValidacionDominioError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})
