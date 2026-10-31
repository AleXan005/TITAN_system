"""Acceso de bajo nivel a SQLite.

Responsabilidad: abrir la conexión, crear las tablas y ejecutar SQL
traduciendo los errores de `sqlite3` a las excepciones propias de la app.
Los repositorios (`sqlite_repo.py`) usan esta clase y nunca importan sqlite3
directamente para manejar errores.

La conexión es única y está protegida con un candado, así es segura si el
frontend usa hilos (Tkinter, Flask, etc.).
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable, Optional

from models.exceptions import DuplicateError, RepositoryError
from utils.logger import get_logger

log = get_logger(__name__)

MEMORY = ":memory:"
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    ticket_type TEXT NOT NULL,
    priority    TEXT NOT NULL,
    status      TEXT NOT NULL,
    project_id  TEXT,
    assignee_id TEXT,
    reporter_id TEXT,
    labels      TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_status   ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tickets_project  ON tickets(project_id);

CREATE TABLE IF NOT EXISTS users (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    role       TEXT NOT NULL,
    active     INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    key         TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    owner_id    TEXT,
    member_ids  TEXT NOT NULL DEFAULT '[]',
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_history (
    id         TEXT PRIMARY KEY,
    ticket_id  TEXT NOT NULL,
    field_name TEXT NOT NULL,
    old_value  TEXT,
    new_value  TEXT,
    changed_by TEXT,
    changed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_history_ticket ON ticket_history(ticket_id);
"""


class Database:
    """Conexión SQLite con creación automática del esquema."""

    def __init__(self, path: str | Path = "data/tickets.db"):
        self.path = str(path)
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Conexión
    # ------------------------------------------------------------------
    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        try:
            if self.path != MEMORY:
                Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.executescript(SCHEMA)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.commit()
        except (sqlite3.Error, OSError) as exc:
            log.error("No se pudo abrir la base de datos '%s': %s", self.path, exc)
            raise RepositoryError(
                f"No se pudo abrir la base de datos '{self.path}': {exc}"
            ) from exc
        log.info("Base de datos lista: %s", self.path)
        self._conn = conn
        return conn

    def close(self) -> None:
        """Cierra la conexión. Se vuelve a abrir sola si se usa de nuevo."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
                log.info("Base de datos cerrada: %s", self.path)

    def __enter__(self) -> "Database":
        self._get_connection()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Ejecución de SQL
    # ------------------------------------------------------------------
    def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
        """Ejecuta una escritura y confirma. Devuelve las filas afectadas."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.execute(sql, tuple(params))
                conn.commit()
                return cursor.rowcount
            except sqlite3.Error as exc:
                conn.rollback()
                raise self._translate(exc) from exc

    def execute_many(self, sql: str, rows: Iterable[Iterable[Any]]) -> int:
        """Ejecuta la misma escritura para varias filas en UNA transacción."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.executemany(sql, [tuple(r) for r in rows])
                conn.commit()
                return cursor.rowcount
            except sqlite3.Error as exc:
                conn.rollback()
                raise self._translate(exc) from exc

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            conn = self._get_connection()
            try:
                return conn.execute(sql, tuple(params)).fetchall()
            except sqlite3.Error as exc:
                raise self._translate(exc) from exc

    def fetch_one(
        self, sql: str, params: Iterable[Any] = ()
    ) -> Optional[sqlite3.Row]:
        with self._lock:
            conn = self._get_connection()
            try:
                return conn.execute(sql, tuple(params)).fetchone()
            except sqlite3.Error as exc:
                raise self._translate(exc) from exc

    # ------------------------------------------------------------------
    # Traducción de errores
    # ------------------------------------------------------------------
    @staticmethod
    def _translate(exc: sqlite3.Error) -> RepositoryError:
        if isinstance(exc, sqlite3.IntegrityError):
            log.warning("Registro duplicado o dato inválido: %s", exc)
            return DuplicateError(f"Registro duplicado o inválido: {exc}")
        log.error("Error de base de datos: %s", exc)
        return RepositoryError(f"Error de base de datos: {exc}")
