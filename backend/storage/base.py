"""Interfaces (clases abstractas) de persistencia.

ESTE ARCHIVO ES EL CONTRATO ENTRE DEV A Y DEV B.

- Dev B programa los servicios contra estas interfaces (y las prueba con
  repositorios falsos en memoria).
- Dev A implementa estas interfaces con SQLite en `sqlite_repo.py`.

Reglas comunes a todas las implementaciones:
- `get*` lanza `*NotFoundError` si no existe; nunca devuelve None.
- `add` lanza `DuplicateError` si el id (o el valor único) ya existe.
- `update` y `delete` lanzan `*NotFoundError` si el registro no existe.
- Cualquier fallo del almacenamiento se traduce a `RepositoryError`.
- Ninguna implementación debe filtrar excepciones propias de su tecnología
  (por ejemplo, de sqlite3) hacia las capas superiores.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from models.enums import Priority, Status, TicketType
from models.history import HistoryEntry
from models.project import Project
from models.ticket import Ticket
from models.user import User


class TicketRepository(ABC):
    """Persistencia de tickets."""

    @abstractmethod
    def add(self, ticket: Ticket) -> Ticket:
        """Guarda un ticket nuevo y lo devuelve."""

    @abstractmethod
    def get(self, ticket_id: str) -> Ticket:
        """Devuelve el ticket. Lanza `TicketNotFoundError` si no existe."""

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        """Reemplaza los datos guardados del ticket (se busca por su id)."""

    @abstractmethod
    def delete(self, ticket_id: str) -> None:
        """Elimina el ticket."""

    @abstractmethod
    def list_all(self) -> list[Ticket]:
        """Todos los tickets, del más antiguo al más nuevo."""

    @abstractmethod
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
        """Filtra tickets. Todos los filtros indicados se combinan con AND.

        - `text` busca (sin distinguir mayúsculas) en título y descripción.
        - `unassigned=True` devuelve solo tickets sin asignado.
        - `open_only=True` excluye los tickets en estado HECHO.
        """

    @abstractmethod
    def count_open_by_assignee(self) -> dict[str, int]:
        """Tickets abiertos (no HECHO) por usuario: {user_id: cantidad}.

        Pensado para la asignación automática por carga de trabajo. Los
        usuarios sin tickets abiertos no aparecen en el diccionario.
        """


class UserRepository(ABC):
    """Persistencia de usuarios."""

    @abstractmethod
    def add(self, user: User) -> User:
        """Guarda un usuario. `DuplicateError` si el correo ya existe."""

    @abstractmethod
    def get(self, user_id: str) -> User:
        """Devuelve el usuario. Lanza `UserNotFoundError` si no existe."""

    @abstractmethod
    def get_by_email(self, email: str) -> User:
        """Busca por correo (sin distinguir mayúsculas)."""

    @abstractmethod
    def update(self, user: User) -> User:
        """Reemplaza los datos guardados del usuario."""

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Elimina al usuario. Normalmente se prefiere `User.deactivate()`."""

    @abstractmethod
    def list_all(self, *, active_only: bool = False) -> list[User]:
        """Todos los usuarios, o solo los activos."""


class ProjectRepository(ABC):
    """Persistencia de proyectos."""

    @abstractmethod
    def add(self, project: Project) -> Project:
        """Guarda un proyecto. `DuplicateError` si la clave ya existe."""

    @abstractmethod
    def get(self, project_id: str) -> Project:
        """Devuelve el proyecto. Lanza `ProjectNotFoundError` si no existe."""

    @abstractmethod
    def get_by_key(self, key: str) -> Project:
        """Busca por clave corta (por ejemplo 'TIT')."""

    @abstractmethod
    def update(self, project: Project) -> Project:
        """Reemplaza los datos guardados del proyecto."""

    @abstractmethod
    def delete(self, project_id: str) -> None:
        """Elimina el proyecto. Normalmente se prefiere `Project.archive()`."""

    @abstractmethod
    def list_all(self, *, active_only: bool = False) -> list[Project]:
        """Todos los proyectos, o solo los activos."""


class HistoryRepository(ABC):
    """Persistencia del historial de cambios de los tickets."""

    @abstractmethod
    def add(self, entry: HistoryEntry) -> HistoryEntry:
        """Guarda una entrada de historial."""

    @abstractmethod
    def add_many(self, entries: list[HistoryEntry]) -> None:
        """Guarda varias entradas de forma atómica (todas o ninguna)."""

    @abstractmethod
    def list_for_ticket(self, ticket_id: str) -> list[HistoryEntry]:
        """Historial de un ticket, de la entrada más antigua a la más nueva.

        Si el ticket no tiene historial devuelve una lista vacía.
        """
