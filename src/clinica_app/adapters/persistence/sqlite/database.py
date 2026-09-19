from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Generator


class SQLiteDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id TEXT PRIMARY KEY, nombre TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL, contacto TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS medicos (
                    id TEXT PRIMARY KEY, nombre TEXT NOT NULL, especialidad TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS citas (
                    id TEXT PRIMARY KEY,
                    paciente_id TEXT NOT NULL REFERENCES pacientes(id),
                    medico_id TEXT NOT NULL REFERENCES medicos(id),
                    fecha_hora TEXT NOT NULL,
                    estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'confirmada', 'cancelada'))
                );
                CREATE UNIQUE INDEX IF NOT EXISTS citas_medico_horario_activo_unico
                    ON citas (medico_id, fecha_hora)
                    WHERE estado IN ('pendiente', 'confirmada');
            """)
