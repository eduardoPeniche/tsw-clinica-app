from clinica_app.application.ports import PacienteRepository
from clinica_app.domain.entities import Paciente


class ListarPacientes:
    def __init__(self, repositorio: PacienteRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self) -> list[Paciente]:
        return self.repositorio.listar()
