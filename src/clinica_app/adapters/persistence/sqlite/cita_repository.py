from datetime import datetime
import sqlite3
from uuid import UUID

from clinica_app.adapters.persistence.sqlite.database import SQLiteDatabase
from clinica_app.application.exceptions import HorarioNoDisponibleError
from clinica_app.domain.entities import Cita, EstadoCita


class SQLiteCitaRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def guardar(self, cita: Cita) -> Cita:
        try:
            with self.database.connect() as c:
                c.execute("INSERT INTO citas VALUES (?, ?, ?, ?, ?)", (str(cita.id), str(cita.paciente_id), str(cita.medico_id), cita.fecha_hora.isoformat(), cita.estado.value))
        except sqlite3.IntegrityError as error:
            if "citas.medico_id, citas.fecha_hora" in str(error):
                raise HorarioNoDisponibleError("El médico ya tiene una cita activa en ese horario.") from error
            raise
        return cita

    def obtener_por_id(self, cita_id: UUID) -> Cita | None:
        with self.database.connect() as c:
            fila = c.execute("SELECT * FROM citas WHERE id=?", (str(cita_id),)).fetchone()
        return self._entidad(fila) if fila else None

    def listar_por_medico(self, medico_id: UUID) -> list[Cita]:
        return self._listar("medico_id", medico_id)

    def listar_por_paciente(self, paciente_id: UUID) -> list[Cita]:
        return self._listar("paciente_id", paciente_id)

    def actualizar(self, cita: Cita) -> Cita:
        with self.database.connect() as c:
            c.execute("UPDATE citas SET paciente_id=?, medico_id=?, fecha_hora=?, estado=? WHERE id=?", (str(cita.paciente_id), str(cita.medico_id), cita.fecha_hora.isoformat(), cita.estado.value, str(cita.id)))
        return cita

    def medico_tiene_cita_activa(self, medico_id: UUID, fecha_hora: datetime) -> bool:
        with self.database.connect() as c:
            fila = c.execute("SELECT 1 FROM citas WHERE medico_id=? AND fecha_hora=? AND estado IN ('pendiente', 'confirmada')", (str(medico_id), fecha_hora.isoformat())).fetchone()
        return fila is not None

    def _listar(self, columna: str, identificador: UUID) -> list[Cita]:
        with self.database.connect() as c:
            filas = c.execute(f"SELECT * FROM citas WHERE {columna}=? ORDER BY fecha_hora, id", (str(identificador),)).fetchall()
        return [self._entidad(fila) for fila in filas]

    @staticmethod
    def _entidad(fila: sqlite3.Row) -> Cita:
        return Cita(
            UUID(fila["paciente_id"]),
            UUID(fila["medico_id"]),
            datetime.fromisoformat(fila["fecha_hora"]),
            EstadoCita(fila["estado"]),
            UUID(fila["id"]),
        )
