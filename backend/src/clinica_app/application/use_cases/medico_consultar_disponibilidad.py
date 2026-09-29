from collections import defaultdict
from datetime import date, timedelta
from uuid import UUID

from clinica_app.application.ports import CitaRepository
from clinica_app.domain.exceptions import ValidacionDominioError
from clinica_app.domain.policies import DisponibilidadAgenda, PoliticaAgenda

MAXIMO_DIAS_DISPONIBILIDAD = 31


class ConsultarDisponibilidadMedico:
    def __init__(
        self, repositorio: CitaRepository, politica_agenda: PoliticaAgenda
    ) -> None:
        self.repositorio = repositorio
        self.politica_agenda = politica_agenda

    def ejecutar(self, medico_id: UUID, fecha: date) -> DisponibilidadAgenda:
        citas = self.repositorio.listar_por_medico_en_fecha(medico_id, fecha)
        return self.politica_agenda.disponibilidad_en_fecha(fecha, citas)

    def ejecutar_en_rango(
        self,
        medico_id: UUID,
        desde: date,
        hasta: date,
    ) -> list[DisponibilidadAgenda]:
        total_dias = (hasta - desde).days + 1
        if total_dias < 1:
            raise ValidacionDominioError(
                "La fecha inicial debe ser anterior o igual a la fecha final."
            )
        if total_dias > MAXIMO_DIAS_DISPONIBILIDAD:
            raise ValidacionDominioError(
                f"El rango de disponibilidad no puede superar {MAXIMO_DIAS_DISPONIBILIDAD} días."
            )

        citas_por_fecha = defaultdict(list)
        for cita in self.repositorio.listar_por_medico_entre_fechas(
            medico_id, desde, hasta
        ):
            fecha_hora = cita.fecha_hora
            if fecha_hora.tzinfo is None:
                fecha_hora = fecha_hora.replace(
                    tzinfo=self.politica_agenda.zona_horaria
                )
            else:
                fecha_hora = fecha_hora.astimezone(self.politica_agenda.zona_horaria)
            fecha_local = fecha_hora.date()
            citas_por_fecha[fecha_local].append(cita)

        return [
            self.politica_agenda.disponibilidad_en_fecha(
                desde + timedelta(days=desplazamiento),
                citas_por_fecha[desde + timedelta(days=desplazamiento)],
            )
            for desplazamiento in range(total_dias)
        ]
