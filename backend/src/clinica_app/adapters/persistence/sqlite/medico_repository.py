import sqlite3
from uuid import UUID

from clinica_app.adapters.persistence.sqlite.database import SQLiteDatabase
from clinica_app.domain.entities import Medico


class SQLiteMedicoRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def guardar(self, medico: Medico) -> Medico:
        with self.database.connect() as c:
            c.execute("INSERT INTO medicos VALUES (?, ?, ?)", (str(medico.id), medico.nombre, medico.especialidad))
        return medico

    def obtener_por_id(self, medico_id: UUID) -> Medico | None:
        with self.database.connect() as c:
            fila = c.execute("SELECT * FROM medicos WHERE id=?", (str(medico_id),)).fetchone()
        return self._entidad(fila) if fila else None

    def listar(self) -> list[Medico]:
        with self.database.connect() as c:
            filas = c.execute("SELECT * FROM medicos ORDER BY nombre, id").fetchall()
        return [self._entidad(fila) for fila in filas]

    def actualizar(self, medico: Medico) -> Medico:
        with self.database.connect() as c:
            c.execute("UPDATE medicos SET nombre=?, especialidad=? WHERE id=?", (medico.nombre, medico.especialidad, str(medico.id)))
        return medico

    def eliminar(self, medico_id: UUID) -> bool:
        with self.database.connect() as c:
            resultado = c.execute("DELETE FROM medicos WHERE id=?", (str(medico_id),))
        return resultado.rowcount > 0

    @staticmethod
    def _entidad(fila: sqlite3.Row) -> Medico:
        return Medico(fila["nombre"], fila["especialidad"], UUID(fila["id"]))
