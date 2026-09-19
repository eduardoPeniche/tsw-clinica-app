from datetime import date
from uuid import UUID

from clinica_app.application.ports import CitaRepository
from clinica_app.domain.policies import DisponibilidadAgenda, PoliticaAgenda


class ConsultarDisponibilidadMedico:
    def __init__(self, repositorio: CitaRepository, politica_agenda: PoliticaAgenda) -> None:
        self.repositorio = repositorio
        self.politica_agenda = politica_agenda

    def ejecutar(self, medico_id: UUID, fecha: date) -> DisponibilidadAgenda:
        citas = self.repositorio.listar_por_medico_en_fecha(medico_id, fecha)
        return self.politica_agenda.disponibilidad_en_fecha(fecha, citas)
