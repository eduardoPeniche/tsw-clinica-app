import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from mcp import Client

from clinica_app.adapters.mcp.server import create_server
from clinica_app.container import build_container


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.container = build_container(Path(self.temporary_directory.name) / "mcp.db")
        self.server = create_server(self.container)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    async def test_expone_las_herramientas_de_la_clinica(self) -> None:
        async with Client(self.server) as client:
            result = await client.list_tools()

        self.assertEqual(
            {tool.name for tool in result.tools},
            {
                "cancelar_cita",
                "actualizar_medico",
                "actualizar_paciente",
                "crear_medico",
                "crear_paciente",
                "consultar_disponibilidad",
                "crear_cita",
                "eliminar_medico",
                "eliminar_paciente",
                "listar_medicos",
                "listar_pacientes",
            },
        )

        herramientas = {tool.name: tool for tool in result.tools}
        self.assertTrue(herramientas["listar_pacientes"].annotations.read_only_hint)
        self.assertFalse(herramientas["crear_paciente"].annotations.read_only_hint)
        self.assertTrue(
            herramientas["eliminar_paciente"].annotations.destructive_hint,
        )

    async def test_crear_cita_usa_el_caso_de_uso_existente(self) -> None:
        paciente = self.container.crear_paciente.ejecutar(
            "Ana López",
            date(1999, 4, 12),
            "ana@example.com",
        )
        medico = self.container.crear_medico.ejecutar("Dra. Ruiz", "Cardiología")

        async with Client(self.server) as client:
            result = await client.call_tool(
                "crear_cita",
                {
                    "paciente_id": str(paciente.id),
                    "medico_id": str(medico.id),
                    "fecha_hora": "2026-10-01T09:00:00",
                },
            )

        self.assertFalse(result.is_error)
        citas = self.container.listar_citas_por_medico.ejecutar(medico.id)
        self.assertEqual(len(citas), 1)
        self.assertEqual(
            citas[0].fecha_hora.replace(tzinfo=None),
            datetime(2026, 10, 1, 9, 0),
        )
        self.assertIsNotNone(citas[0].fecha_hora.tzinfo)

    async def test_crud_de_pacientes_y_medicos_usa_los_casos_de_uso_existentes(
        self,
    ) -> None:
        async with Client(self.server) as client:
            paciente_creado = await client.call_tool(
                "crear_paciente",
                {
                    "nombre": "Ana López",
                    "fecha_nacimiento": "1999-04-12",
                    "contacto": "ana@example.com",
                },
            )
            paciente_id = paciente_creado.structured_content["id"]
            paciente_actualizado = await client.call_tool(
                "actualizar_paciente",
                {
                    "paciente_id": paciente_id,
                    "nombre": "Ana García",
                    "fecha_nacimiento": "1999-04-12",
                    "contacto": "ana.garcia@example.com",
                },
            )
            paciente_eliminado = await client.call_tool(
                "eliminar_paciente",
                {"paciente_id": paciente_id},
            )

            medico_creado = await client.call_tool(
                "crear_medico",
                {"nombre": "Dr. Ruiz", "especialidad": "Cardiología"},
            )
            medico_id = medico_creado.structured_content["id"]
            medico_actualizado = await client.call_tool(
                "actualizar_medico",
                {
                    "medico_id": medico_id,
                    "nombre": "Dra. Ruiz",
                    "especialidad": "Medicina interna",
                },
            )
            medico_eliminado = await client.call_tool(
                "eliminar_medico",
                {"medico_id": medico_id},
            )

        self.assertEqual(
            paciente_actualizado.structured_content["nombre"], "Ana García"
        )
        self.assertTrue(paciente_eliminado.structured_content["eliminado"])
        self.assertEqual(medico_actualizado.structured_content["nombre"], "Dra. Ruiz")
        self.assertTrue(medico_eliminado.structured_content["eliminado"])
