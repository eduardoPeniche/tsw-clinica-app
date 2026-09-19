import os
from dataclasses import dataclass
from pathlib import Path

from clinica_app.adapters.persistence.sqlite.cita_repository import SQLiteCitaRepository
from clinica_app.adapters.persistence.sqlite.database import SQLiteDatabase
from clinica_app.adapters.persistence.sqlite.medico_repository import SQLiteMedicoRepository
from clinica_app.adapters.persistence.sqlite.paciente_repository import (
    SQLitePacienteRepository,
)
from clinica_app.application.use_cases import (
    ActualizarMedico,
    ActualizarPaciente,
    CancelarCita,
    CrearCita,
    CrearMedico,
    CrearPaciente,
    EliminarMedico,
    EliminarPaciente,
    ListarCitasPorMedico,
    ListarCitasPorPaciente,
    ListarMedicos,
    ListarPacientes,
    ObtenerMedico,
    ObtenerPaciente,
)


@dataclass
class ApplicationContainer:
    crear_paciente: CrearPaciente
    obtener_paciente: ObtenerPaciente
    listar_pacientes: ListarPacientes
    actualizar_paciente: ActualizarPaciente
    eliminar_paciente: EliminarPaciente
    crear_medico: CrearMedico
    obtener_medico: ObtenerMedico
    listar_medicos: ListarMedicos
    actualizar_medico: ActualizarMedico
    eliminar_medico: EliminarMedico
    crear_cita: CrearCita
    cancelar_cita: CancelarCita
    listar_citas_por_medico: ListarCitasPorMedico
    listar_citas_por_paciente: ListarCitasPorPaciente


def build_container(database_path: str | Path | None = None) -> ApplicationContainer:
    path = database_path or os.getenv("DATABASE_PATH", "/data/clinica.db")
    database = SQLiteDatabase(path)
    database.initialize()

    pacientes = SQLitePacienteRepository(database)
    medicos = SQLiteMedicoRepository(database)
    citas = SQLiteCitaRepository(database)

    return ApplicationContainer(
        crear_paciente=CrearPaciente(pacientes),
        obtener_paciente=ObtenerPaciente(pacientes),
        listar_pacientes=ListarPacientes(pacientes),
        actualizar_paciente=ActualizarPaciente(pacientes),
        eliminar_paciente=EliminarPaciente(pacientes),
        crear_medico=CrearMedico(medicos),
        obtener_medico=ObtenerMedico(medicos),
        listar_medicos=ListarMedicos(medicos),
        actualizar_medico=ActualizarMedico(medicos),
        eliminar_medico=EliminarMedico(medicos),
        crear_cita=CrearCita(citas, pacientes, medicos),
        cancelar_cita=CancelarCita(citas),
        listar_citas_por_medico=ListarCitasPorMedico(citas),
        listar_citas_por_paciente=ListarCitasPorPaciente(citas),
    )
