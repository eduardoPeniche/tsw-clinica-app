from datetime import date

from clinica_app.application.ports import PacienteRepository
from clinica_app.domain.entities import Paciente


class CrearPaciente:
    def __init__(self, repositorio: PacienteRepository) -> None:
        self.repositorio = repositorio

    def ejecutar(
        self,
        nombre: str,
        fecha_nacimiento: date,
        contacto: str,
    ) -> Paciente:
        paciente = Paciente(nombre, fecha_nacimiento, contacto)
        return self.repositorio.guardar(paciente)
