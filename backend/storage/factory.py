"""Punto único para construir todos los repositorios SQLite juntos.

Dev B (y la fachada) usan esto en lugar de crear cada repositorio a mano:

    storage = create_sqlite_storage(settings.db_path)
    service = TicketService(storage.tickets, storage.history, notifier)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from storage.base import (
    HistoryRepository,
    ProjectRepository,
    TicketRepository,
    UserRepository,
)
from storage.database import Database
from storage.sqlite_repo import (
    SQLiteHistoryRepository,
    SQLiteProjectRepository,
    SQLiteTicketRepository,
    SQLiteUserRepository,
)


@dataclass
class Storage:
    """Agrupa la base de datos y todos sus repositorios."""

    db: Database
    tickets: TicketRepository
    users: UserRepository
    projects: ProjectRepository
    history: HistoryRepository

    def close(self) -> None:
        self.db.close()


def create_sqlite_storage(db_path: str | Path = "data/tickets.db") -> Storage:
    """Crea la base (si no existe) y devuelve todos los repositorios.

    Usa `":memory:"` como ruta para una base temporal, ideal para pruebas.
    """
    db = Database(db_path)
    return Storage(
        db=db,
        tickets=SQLiteTicketRepository(db),
        users=SQLiteUserRepository(db),
        projects=SQLiteProjectRepository(db),
        history=SQLiteHistoryRepository(db),
    )
