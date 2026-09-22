import sqlite3
from datetime import date
from uuid import UUID

from clinica_app.adapters.persistence.sqlite.database import SQLiteDatabase
from clinica_app.domain.entities import Paciente


class SQLitePacienteRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def guardar(self, paciente: Paciente) -> Paciente:
        with self.database.connect() as c:
            c.execute(
                "INSERT INTO pacientes VALUES (?, ?, ?, ?)",
                (
                    str(paciente.id),
                    paciente.nombre,
                    paciente.fecha_nacimiento.isoformat(),
                    paciente.contacto,
                ),
            )
        return paciente

    def obtener_por_id(self, paciente_id: UUID) -> Paciente | None:
        with self.database.connect() as c:
            fila = c.execute(
                "SELECT * FROM pacientes WHERE id = ?", (str(paciente_id),)
            ).fetchone()
        return self._entidad(fila) if fila else None

    def listar(self) -> list[Paciente]:
        with self.database.connect() as c:
            filas = c.execute("SELECT * FROM pacientes ORDER BY nombre, id").fetchall()
        return [self._entidad(fila) for fila in filas]

    def actualizar(self, paciente: Paciente) -> Paciente:
        with self.database.connect() as c:
            c.execute(
                "UPDATE pacientes SET nombre=?, fecha_nacimiento=?, contacto=? WHERE id=?",
                (
                    paciente.nombre,
                    paciente.fecha_nacimiento.isoformat(),
                    paciente.contacto,
                    str(paciente.id),
                ),
            )
        return paciente

    def eliminar(self, paciente_id: UUID) -> bool:
        with self.database.connect() as c:
            resultado = c.execute(
                "DELETE FROM pacientes WHERE id=?", (str(paciente_id),)
            )
        return resultado.rowcount > 0

    @staticmethod
    def _entidad(fila: sqlite3.Row) -> Paciente:
        return Paciente(
            fila["nombre"],
            date.fromisoformat(fila["fecha_nacimiento"]),
            fila["contacto"],
            UUID(fila["id"]),
        )
