"""Modelo de dominio `HistoryEntry`: historial de cambios de un ticket.

Cada entrada responde a: ¿qué ticket?, ¿qué campo?, ¿de qué valor a cuál?,
¿quién lo cambió? y ¿cuándo?

Este módulo NO guarda nada. Solo sabe construir las entradas comparando dos
versiones de un ticket. Quien las guarda es `storage` (HistoryRepository) y
quien decide cuándo registrarlas son los servicios (Dev B).

Uso típico en un servicio:

    old = tickets.get(ticket_id)          # versión guardada en la base
    new = tickets.get(ticket_id)          # copia independiente para editar
    new.change_status("revision")
    tickets.update(new)
    history.add_many(build_entries(old, new, changed_by=user_id))
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from models.exceptions import ValidationError
from models.ticket import Ticket

# Campos del ticket cuyos cambios se registran.
TRACKED_FIELDS: tuple[str, ...] = (
    "title",
    "description",
    "ticket_type",
    "priority",
    "status",
    "project_id",
    "assignee_id",
    "labels",
)

CREATED_FIELD = "created"


def _now() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


def _stringify(value: Any) -> Optional[str]:
    """Convierte cualquier valor del ticket a texto comparable (o None)."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, (list, tuple)):
        text = ", ".join(str(item) for item in value)
    else:
        text = str(value)
    return text if text != "" else None


@dataclass
class HistoryEntry:
    """Un cambio individual sobre un campo de un ticket."""

    ticket_id: str
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[str] = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    changed_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.ticket_id or not str(self.ticket_id).strip():
            raise ValidationError("La entrada de historial necesita un ticket_id.")
        if not self.field_name or not str(self.field_name).strip():
            raise ValidationError("La entrada de historial necesita un campo.")

    # ------------------------------------------------------------------
    # Constructores de conveniencia
    # ------------------------------------------------------------------
    @classmethod
    def for_creation(
        cls, ticket: Ticket, changed_by: Optional[str] = None
    ) -> "HistoryEntry":
        """Entrada que registra la creación de un ticket."""
        return cls(
            ticket_id=ticket.id,
            field_name=CREATED_FIELD,
            old_value=None,
            new_value=ticket.title,
            changed_by=changed_by,
        )

    # ------------------------------------------------------------------
    # Serialización (la usan storage/ y api/)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryEntry":
        data = dict(data)
        if isinstance(data.get("changed_at"), str):
            data["changed_at"] = datetime.fromisoformat(data["changed_at"])
        return cls(**data)

    def __str__(self) -> str:
        quien = self.changed_by or "sistema"
        return (
            f"{self.changed_at:%Y-%m-%d %H:%M} | {quien} cambió "
            f"{self.field_name}: {self.old_value!r} -> {self.new_value!r}"
        )


def build_entries(
    old: Ticket, new: Ticket, changed_by: Optional[str] = None
) -> list[HistoryEntry]:
    """Compara dos versiones del MISMO ticket y devuelve una entrada por campo
    que cambió. Si no hay diferencias, devuelve una lista vacía.

    `old` debe ser una copia independiente (por ejemplo, un `get()` hecho antes
    de modificar). Si es el mismo objeto que `new`, nunca habrá diferencias.
    """
    if old.id != new.id:
        raise ValidationError("Solo se pueden comparar versiones del mismo ticket.")

    entries: list[HistoryEntry] = []
    for name in TRACKED_FIELDS:
        before = _stringify(getattr(old, name))
        after = _stringify(getattr(new, name))
        if before != after:
            entries.append(
                HistoryEntry(
                    ticket_id=new.id,
                    field_name=name,
                    old_value=before,
                    new_value=after,
                    changed_by=changed_by,
                )
            )
    return entries
