"""Implementaciones SQLite de los repositorios definidos en `base.py`.

Cada clase traduce entre objetos del dominio (Ticket, User, Project,
HistoryEntry) y filas de la base de datos. No contiene lógica de negocio.
"""

from __future__ import annotations

import json
import sqlite3
from enum import Enum
from typing import Any, Optional

from models.enums import Priority, Status, TicketType
from models.exceptions import (
    DuplicateError,
    ProjectNotFoundError,
    TicketNotFoundError,
    UserNotFoundError,
)
from models.history import HistoryEntry
from models.project import Project
from models.ticket import Ticket
from models.user import User
from storage.base import (
    HistoryRepository,
    ProjectRepository,
    TicketRepository,
    UserRepository,
)
from storage.database import Database
from utils.logger import get_logger

log = get_logger(__name__)


def _plain(value: Any) -> Any:
    """Convierte un Enum a su valor de texto; deja el resto igual."""
    return value.value if isinstance(value, Enum) else value


def _escape_like(text: str) -> str:
    """Escapa los comodines de LIKE para que se busquen como texto literal."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# ----------------------------------------------------------------------
# Tickets
# ----------------------------------------------------------------------
_TICKET_COLUMNS = (
    "id",
    "title",
    "description",
    "ticket_type",
    "priority",
    "status",
    "project_id",
    "assignee_id",
    "reporter_id",
    "labels",
    "created_at",
    "updated_at",
)


class SQLiteTicketRepository(TicketRepository):
    def __init__(self, db: Database):
        self._db = db

    # -- conversión -----------------------------------------------------
    @staticmethod
    def _to_params(ticket: Ticket) -> dict[str, Any]:
        data = ticket.to_dict()
        data["labels"] = json.dumps(data["labels"], ensure_ascii=False)
        return data

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Ticket:
        data = dict(row)
        data["labels"] = json.loads(data["labels"] or "[]")
        return Ticket.from_dict(data)

    # -- operaciones ----------------------------------------------------
    def add(self, ticket: Ticket) -> Ticket:
        params = self._to_params(ticket)
        columns = ", ".join(_TICKET_COLUMNS)
        marks = ", ".join("?" for _ in _TICKET_COLUMNS)
        try:
            self._db.execute(
                f"INSERT INTO tickets ({columns}) VALUES ({marks})",
                [params[c] for c in _TICKET_COLUMNS],
            )
        except DuplicateError as exc:
            raise DuplicateError(f"Ya existe un ticket con id '{ticket.id}'.") from exc
        log.info("Ticket creado: %s", ticket.id)
        return ticket

    def get(self, ticket_id: str) -> Ticket:
        row = self._db.fetch_one("SELECT * FROM tickets WHERE id = ?", [ticket_id])
        if row is None:
            raise TicketNotFoundError(ticket_id)
        return self._from_row(row)

    def update(self, ticket: Ticket) -> Ticket:
        params = self._to_params(ticket)
        columns = [c for c in _TICKET_COLUMNS if c != "id"]
        assignments = ", ".join(f"{c} = ?" for c in columns)
        changed = self._db.execute(
            f"UPDATE tickets SET {assignments} WHERE id = ?",
            [params[c] for c in columns] + [ticket.id],
        )
        if changed == 0:
            raise TicketNotFoundError(ticket.id)
        log.info("Ticket actualizado: %s", ticket.id)
        return ticket

    def delete(self, ticket_id: str) -> None:
        if self._db.execute("DELETE FROM tickets WHERE id = ?", [ticket_id]) == 0:
            raise TicketNotFoundError(ticket_id)
        log.info("Ticket eliminado: %s", ticket_id)

    def list_all(self) -> list[Ticket]:
        rows = self._db.fetch_all("SELECT * FROM tickets ORDER BY created_at, rowid")
        return [self._from_row(r) for r in rows]

    def find(
        self,
        *,
        status: Optional[Status | str] = None,
        priority: Optional[Priority | str] = None,
        ticket_type: Optional[TicketType | str] = None,
        assignee_id: Optional[str] = None,
        project_id: Optional[str] = None,
        text: Optional[str] = None,
        unassigned: bool = False,
        open_only: bool = False,
    ) -> list[Ticket]:
        conditions: list[str] = []
        params: list[Any] = []

        for column, value in (
            ("status", status),
            ("priority", priority),
            ("ticket_type", ticket_type),
            ("assignee_id", assignee_id),
            ("project_id", project_id),
        ):
            if value is not None:
                conditions.append(f"{column} = ?")
                params.append(_plain(value))

        if unassigned:
            conditions.append("assignee_id IS NULL")
        if open_only:
            conditions.append("status != ?")
            params.append(Status.HECHO.value)
        if text:
            pattern = f"%{_escape_like(text.strip())}%"
            conditions.append(
                "(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')"
            )
            params.extend([pattern, pattern])

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self._db.fetch_all(
            f"SELECT * FROM tickets{where} ORDER BY created_at, rowid", params
        )
        return [self._from_row(r) for r in rows]

    def count_open_by_assignee(self) -> dict[str, int]:
        rows = self._db.fetch_all(
            "SELECT assignee_id, COUNT(*) AS total FROM tickets "
            "WHERE assignee_id IS NOT NULL AND status != ? "
            "GROUP BY assignee_id",
            [Status.HECHO.value],
        )
        return {row["assignee_id"]: row["total"] for row in rows}


# ----------------------------------------------------------------------
# Usuarios
# ----------------------------------------------------------------------
class SQLiteUserRepository(UserRepository):
    _COLUMNS = ("id", "name", "email", "role", "active", "created_at")

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _from_row(row: sqlite3.Row) -> User:
        data = dict(row)
        data["active"] = bool(data["active"])
        return User.from_dict(data)

    def _values(self, user: User) -> dict[str, Any]:
        data = user.to_dict()
        data["active"] = int(data["active"])
        return data

    def add(self, user: User) -> User:
        data = self._values(user)
        columns = ", ".join(self._COLUMNS)
        marks = ", ".join("?" for _ in self._COLUMNS)
        try:
            self._db.execute(
                f"INSERT INTO users ({columns}) VALUES ({marks})",
                [data[c] for c in self._COLUMNS],
            )
        except DuplicateError as exc:
            raise DuplicateError(
                f"Ya existe un usuario con el correo '{user.email}' o el id '{user.id}'."
            ) from exc
        log.info("Usuario creado: %s", user.id)
        return user

    def get(self, user_id: str) -> User:
        row = self._db.fetch_one("SELECT * FROM users WHERE id = ?", [user_id])
        if row is None:
            raise UserNotFoundError(user_id)
        return self._from_row(row)

    def get_by_email(self, email: str) -> User:
        row = self._db.fetch_one(
            "SELECT * FROM users WHERE email = ?", [email.strip().lower()]
        )
        if row is None:
            raise UserNotFoundError(email)
        return self._from_row(row)

    def update(self, user: User) -> User:
        data = self._values(user)
        columns = [c for c in self._COLUMNS if c != "id"]
        assignments = ", ".join(f"{c} = ?" for c in columns)
        try:
            changed = self._db.execute(
                f"UPDATE users SET {assignments} WHERE id = ?",
                [data[c] for c in columns] + [user.id],
            )
        except DuplicateError as exc:
            raise DuplicateError(
                f"Ya existe otro usuario con el correo '{user.email}'."
            ) from exc
        if changed == 0:
            raise UserNotFoundError(user.id)
        log.info("Usuario actualizado: %s", user.id)
        return user

    def delete(self, user_id: str) -> None:
        if self._db.execute("DELETE FROM users WHERE id = ?", [user_id]) == 0:
            raise UserNotFoundError(user_id)
        log.info("Usuario eliminado: %s", user_id)

    def list_all(self, *, active_only: bool = False) -> list[User]:
        where = " WHERE active = 1" if active_only else ""
        rows = self._db.fetch_all(
            f"SELECT * FROM users{where} ORDER BY created_at, rowid"
        )
        return [self._from_row(r) for r in rows]


# ----------------------------------------------------------------------
# Proyectos
# ----------------------------------------------------------------------
class SQLiteProjectRepository(ProjectRepository):
    _COLUMNS = (
        "id",
        "name",
        "key",
        "description",
        "owner_id",
        "member_ids",
        "active",
        "created_at",
    )

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Project:
        data = dict(row)
        data["member_ids"] = json.loads(data["member_ids"] or "[]")
        data["active"] = bool(data["active"])
        return Project.from_dict(data)

    @staticmethod
    def _values(project: Project) -> dict[str, Any]:
        data = project.to_dict()
        data["member_ids"] = json.dumps(data["member_ids"], ensure_ascii=False)
        data["active"] = int(data["active"])
        return data

    def add(self, project: Project) -> Project:
        data = self._values(project)
        columns = ", ".join(self._COLUMNS)
        marks = ", ".join("?" for _ in self._COLUMNS)
        try:
            self._db.execute(
                f"INSERT INTO projects ({columns}) VALUES ({marks})",
                [data[c] for c in self._COLUMNS],
            )
        except DuplicateError as exc:
            raise DuplicateError(
                f"Ya existe un proyecto con la clave '{project.key}' o el id '{project.id}'."
            ) from exc
        log.info("Proyecto creado: %s (%s)", project.key, project.id)
        return project

    def get(self, project_id: str) -> Project:
        row = self._db.fetch_one("SELECT * FROM projects WHERE id = ?", [project_id])
        if row is None:
            raise ProjectNotFoundError(project_id)
        return self._from_row(row)

    def get_by_key(self, key: str) -> Project:
        row = self._db.fetch_one(
            "SELECT * FROM projects WHERE key = ?", [key.strip().upper()]
        )
        if row is None:
            raise ProjectNotFoundError(key)
        return self._from_row(row)

    def update(self, project: Project) -> Project:
        data = self._values(project)
        columns = [c for c in self._COLUMNS if c != "id"]
        assignments = ", ".join(f"{c} = ?" for c in columns)
        try:
            changed = self._db.execute(
                f"UPDATE projects SET {assignments} WHERE id = ?",
                [data[c] for c in columns] + [project.id],
            )
        except DuplicateError as exc:
            raise DuplicateError(
                f"Ya existe otro proyecto con la clave '{project.key}'."
            ) from exc
        if changed == 0:
            raise ProjectNotFoundError(project.id)
        log.info("Proyecto actualizado: %s", project.id)
        return project

    def delete(self, project_id: str) -> None:
        if self._db.execute("DELETE FROM projects WHERE id = ?", [project_id]) == 0:
            raise ProjectNotFoundError(project_id)
        log.info("Proyecto eliminado: %s", project_id)

    def list_all(self, *, active_only: bool = False) -> list[Project]:
        where = " WHERE active = 1" if active_only else ""
        rows = self._db.fetch_all(
            f"SELECT * FROM projects{where} ORDER BY created_at, rowid"
        )
        return [self._from_row(r) for r in rows]


# ----------------------------------------------------------------------
# Historial
# ----------------------------------------------------------------------
class SQLiteHistoryRepository(HistoryRepository):
    _COLUMNS = (
        "id",
        "ticket_id",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "changed_at",
    )
    _INSERT = (
        f"INSERT INTO ticket_history ({', '.join(_COLUMNS)}) "
        f"VALUES ({', '.join('?' for _ in _COLUMNS)})"
    )

    def __init__(self, db: Database):
        self._db = db

    def _row_values(self, entry: HistoryEntry) -> list[Any]:
        data = entry.to_dict()
        return [data[c] for c in self._COLUMNS]

    def add(self, entry: HistoryEntry) -> HistoryEntry:
        self._db.execute(self._INSERT, self._row_values(entry))
        return entry

    def add_many(self, entries: list[HistoryEntry]) -> None:
        if not entries:
            return
        self._db.execute_many(self._INSERT, [self._row_values(e) for e in entries])
        log.debug("Historial: %d entradas guardadas", len(entries))

    def list_for_ticket(self, ticket_id: str) -> list[HistoryEntry]:
        rows = self._db.fetch_all(
            "SELECT * FROM ticket_history WHERE ticket_id = ? "
            "ORDER BY changed_at, rowid",
            [ticket_id],
        )
        return [HistoryEntry.from_dict(dict(r)) for r in rows]
