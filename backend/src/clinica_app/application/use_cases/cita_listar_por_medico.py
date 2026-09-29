from datetime import date
from uuid import UUID

from clinica_app.application.ports import CitaRepository
from clinica_app.domain.entities import Cita
from clinica_app.domain.exceptions import ValidacionDominioError

MAXIMO_DIAS_CITAS = 31


class ListarCitasPorMedico:
    def __init__(self, repositorio: CitaRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, medico_id: UUID, fecha: date | None = None) -> list[Cita]:
        if fecha is not None:
            return self.repositorio.listar_por_medico_en_fecha(medico_id, fecha)
        return self.repositorio.listar_por_medico(medico_id)

    def ejecutar_en_rango(
        self, medico_id: UUID, desde: date, hasta: date
    ) -> list[Cita]:
        total_dias = (hasta - desde).days + 1
        if total_dias < 1:
            raise ValidacionDominioError(
                "La fecha inicial debe ser anterior o igual a la fecha final."
            )
        if total_dias > MAXIMO_DIAS_CITAS:
            raise ValidacionDominioError(
                f"El rango de citas no puede superar {MAXIMO_DIAS_CITAS} días."
            )
        return self.repositorio.listar_por_medico_entre_fechas(medico_id, desde, hasta)
