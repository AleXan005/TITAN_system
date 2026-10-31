"""Capa de persistencia: interfaces abstractas e implementación SQLite."""

from storage.base import (
    HistoryRepository,
    ProjectRepository,
    TicketRepository,
    UserRepository,
)
from storage.factory import Storage, create_sqlite_storage

__all__ = [
    "HistoryRepository",
    "ProjectRepository",
    "TicketRepository",
    "UserRepository",
    "Storage",
    "create_sqlite_storage",
]
