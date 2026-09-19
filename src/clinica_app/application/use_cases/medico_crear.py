from clinica_app.application.ports import MedicoRepository
from clinica_app.domain.entities import Medico


class CrearMedico:
    def __init__(self, repositorio: MedicoRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(self, nombre: str, especialidad: str) -> Medico:
        medico = Medico(nombre, especialidad)
        return self.repositorio.guardar(medico)
