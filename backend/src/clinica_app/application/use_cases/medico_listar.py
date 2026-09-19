from clinica_app.application.ports import MedicoRepository
from clinica_app.domain.entities import Medico


class ListarMedicos:
    def __init__(self, repositorio: MedicoRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self) -> list[Medico]:
        return self.repositorio.listar()
