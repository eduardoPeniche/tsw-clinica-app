from datetime import date, datetime
from typing import Any
from uuid import UUID

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from clinica_app.container import ApplicationContainer, build_container
from clinica_app.domain.entities import Cita, Medico, Paciente
from clinica_app.domain.policies import DisponibilidadAgenda


READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)
MUTATION = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)
DELETION = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=False,
    open_world_hint=False,
)


def _paciente_output(paciente: Paciente) -> dict[str, str]:
    return {
        "id": str(paciente.id),
        "nombre": paciente.nombre,
        "fecha_nacimiento": paciente.fecha_nacimiento.isoformat(),
        "contacto": paciente.contacto,
    }


def _medico_output(medico: Medico) -> dict[str, str]:
    return {
        "id": str(medico.id),
        "nombre": medico.nombre,
        "especialidad": medico.especialidad,
    }


def _cita_output(cita: Cita) -> dict[str, str]:
    return {
        "id": str(cita.id),
        "paciente_id": str(cita.paciente_id),
        "medico_id": str(cita.medico_id),
        "fecha_hora": cita.fecha_hora.isoformat(),
        "estado": cita.estado.value,
    }


def _disponibilidad_output(disponibilidad: DisponibilidadAgenda) -> dict[str, Any]:
    return {
        "fecha": disponibilidad.fecha.isoformat(),
        "zona_horaria": disponibilidad.zona_horaria,
        "slots": [
            {
                "inicio": slot.inicio.strftime("%H:%M"),
                "fin": slot.fin.strftime("%H:%M"),
                "estado": slot.estado.value,
            }
            for slot in disponibilidad.slots
        ],
        "slot_recomendado": (
            disponibilidad.slot_recomendado.strftime("%H:%M")
            if disponibilidad.slot_recomendado
            else None
        ),
    }


def create_server(services: ApplicationContainer | None = None) -> MCPServer:
    """Construye el servidor MCP; las pruebas pueden inyectar su propio contenedor."""
    container = services or build_container()
    server = MCPServer(
        "Clinica App",
        instructions=(
            "Usa las herramientas de consulta antes de modificar datos. Confirma con "
            "la persona usuaria los datos de cualquier operación que cree, actualice, "
            "elimine o cancele un recurso."
        ),
    )

    @server.tool(annotations=READ_ONLY)
    def listar_pacientes() -> list[dict[str, str]]:
        """Lista los pacientes registrados con sus identificadores."""
        return [
            _paciente_output(paciente)
            for paciente in container.listar_pacientes.ejecutar()
        ]

    @server.tool(annotations=MUTATION)
    def crear_paciente(
        nombre: str,
        fecha_nacimiento: date,
        contacto: str,
    ) -> dict[str, str]:
        """Crea un paciente tras confirmar los datos con la persona usuaria."""
        paciente = container.crear_paciente.ejecutar(
            nombre,
            fecha_nacimiento,
            contacto,
        )
        return _paciente_output(paciente)

    @server.tool(annotations=MUTATION)
    def actualizar_paciente(
        paciente_id: UUID,
        nombre: str,
        fecha_nacimiento: date,
        contacto: str,
    ) -> dict[str, str]:
        """Actualiza un paciente tras confirmar todos sus datos."""
        paciente = container.actualizar_paciente.ejecutar(
            paciente_id,
            nombre,
            fecha_nacimiento,
            contacto,
        )
        return _paciente_output(paciente)

    @server.tool(annotations=DELETION)
    def eliminar_paciente(paciente_id: UUID) -> dict[str, str | bool]:
        """Elimina un paciente tras confirmar la operación con la persona usuaria."""
        container.eliminar_paciente.ejecutar(paciente_id)
        return {"id": str(paciente_id), "eliminado": True}

    @server.tool(annotations=READ_ONLY)
    def listar_medicos() -> list[dict[str, str]]:
        """Lista los médicos registrados con sus identificadores y especialidad."""
        return [
            _medico_output(medico)
            for medico in container.listar_medicos.ejecutar()
        ]

    @server.tool(annotations=MUTATION)
    def crear_medico(nombre: str, especialidad: str) -> dict[str, str]:
        """Crea un médico tras confirmar los datos con la persona usuaria."""
        medico = container.crear_medico.ejecutar(nombre, especialidad)
        return _medico_output(medico)

    @server.tool(annotations=MUTATION)
    def actualizar_medico(
        medico_id: UUID,
        nombre: str,
        especialidad: str,
    ) -> dict[str, str]:
        """Actualiza un médico tras confirmar todos sus datos."""
        medico = container.actualizar_medico.ejecutar(
            medico_id,
            nombre,
            especialidad,
        )
        return _medico_output(medico)

    @server.tool(annotations=DELETION)
    def eliminar_medico(medico_id: UUID) -> dict[str, str | bool]:
        """Elimina un médico tras confirmar la operación con la persona usuaria."""
        container.eliminar_medico.ejecutar(medico_id)
        return {"id": str(medico_id), "eliminado": True}

    @server.tool(annotations=READ_ONLY)
    def consultar_disponibilidad(medico_id: UUID, fecha: date) -> dict[str, Any]:
        """Consulta los slots de agenda de un médico para una fecha."""
        disponibilidad = container.consultar_disponibilidad_medico.ejecutar(
            medico_id,
            fecha,
        )
        return _disponibilidad_output(disponibilidad)

    @server.tool(annotations=MUTATION)
    def crear_cita(
        paciente_id: UUID,
        medico_id: UUID,
        fecha_hora: datetime,
    ) -> dict[str, str]:
        """Crea una cita válida tras confirmar los datos con la persona usuaria."""
        cita = container.crear_cita.ejecutar(paciente_id, medico_id, fecha_hora)
        return _cita_output(cita)

    @server.tool(annotations=MUTATION)
    def cancelar_cita(cita_id: UUID) -> dict[str, str]:
        """Cancela una cita tras confirmar la cancelación con la persona usuaria."""
        cita = container.cancelar_cita.ejecutar(cita_id)
        return _cita_output(cita)

    return server


if __name__ == "__main__":
    create_server().run()
