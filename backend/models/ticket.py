"""Modelo de dominio `Ticket`.

Responsabilidad: representar un ticket y validar sus propios datos.
NO sabe nada de bases de datos, reglas de automatización ni interfaz.
- La persistencia vive en `storage/`.
- Las transiciones válidas de estado viven en `automation/workflow.py`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from models.enums import Priority, Status, TicketType
from models.exceptions import ValidationError

TITLE_MAX_LENGTH = 120


def _now() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


@dataclass
class Ticket:
    """Ticket de desarrollo de software."""

    title: str
    description: str = ""
    ticket_type: TicketType = TicketType.TAREA
    priority: Priority = Priority.MEDIA
    status: Status = Status.NUEVO
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None
    reporter_id: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    # ------------------------------------------------------------------
    # Inicialización y validación
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        self.title = self._clean_title(self.title)
        self.description = (self.description or "").strip()
        # Acepta strings ("alta") y los convierte al enum correspondiente.
        self.ticket_type = self._to_enum(TicketType, self.ticket_type, "tipo")
        self.priority = self._to_enum(Priority, self.priority, "prioridad")
        self.status = self._to_enum(Status, self.status, "estado")
        self.labels = self._clean_labels(self.labels)

    @staticmethod
    def _clean_title(title: str) -> str:
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("El título del ticket no puede estar vacío.")
        title = title.strip()
        if len(title) > TITLE_MAX_LENGTH:
            raise ValidationError(
                f"El título no puede superar {TITLE_MAX_LENGTH} caracteres."
            )
        return title

    @staticmethod
    def _to_enum(enum_cls: type, value: Any, name: str):
        if isinstance(value, enum_cls):
            return value
        try:
            return enum_cls(value)
        except ValueError:
            valid = ", ".join(e.value for e in enum_cls)
            raise ValidationError(
                f"Valor de {name} inválido: '{value}'. Opciones: {valid}."
            ) from None

    @staticmethod
    def _clean_labels(labels: list[str]) -> list[str]:
        cleaned: list[str] = []
        for label in labels or []:
            label = str(label).strip().lower()
            if label and label not in cleaned:
                cleaned.append(label)
        return cleaned

    def _touch(self) -> None:
        """Actualiza la fecha de última modificación."""
        self.updated_at = _now()

    # ------------------------------------------------------------------
    # Operaciones sobre el ticket
    # ------------------------------------------------------------------
    def update_details(
        self, title: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        """Edita título y/o descripción."""
        if title is not None:
            self.title = self._clean_title(title)
        if description is not None:
            self.description = description.strip()
        self._touch()

    def change_status(self, new_status: Status | str) -> None:
        """Cambia el estado.

        Solo valida que el valor sea un estado real. Si la transición es
        permitida o no lo decide el workflow (Dev B) ANTES de llamar aquí.
        """
        self.status = self._to_enum(Status, new_status, "estado")
        self._touch()

    def change_priority(self, new_priority: Priority | str) -> None:
        self.priority = self._to_enum(Priority, new_priority, "prioridad")
        self._touch()

    def assign(self, user_id: str) -> None:
        """Asigna el ticket a un usuario."""
        if not user_id or not str(user_id).strip():
            raise ValidationError("El id del asignado no puede estar vacío.")
        self.assignee_id = str(user_id).strip()
        self._touch()

    def unassign(self) -> None:
        self.assignee_id = None
        self._touch()

    def add_label(self, label: str) -> None:
        label = str(label).strip().lower()
        if not label:
            raise ValidationError("La etiqueta no puede estar vacía.")
        if label not in self.labels:
            self.labels.append(label)
            self._touch()

    def remove_label(self, label: str) -> None:
        label = str(label).strip().lower()
        if label in self.labels:
            self.labels.remove(label)
            self._touch()

    # ------------------------------------------------------------------
    # Propiedades de consulta
    # ------------------------------------------------------------------
    @property
    def is_assigned(self) -> bool:
        return self.assignee_id is not None

    @property
    def is_closed(self) -> bool:
        return self.status == Status.HECHO

    # ------------------------------------------------------------------
    # Serialización (la usan storage/ y api/)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Convierte el ticket a un diccionario con tipos simples."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ticket_type": self.ticket_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "project_id": self.project_id,
            "assignee_id": self.assignee_id,
            "reporter_id": self.reporter_id,
            "labels": list(self.labels),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ticket":
        """Reconstruye un ticket desde un diccionario (inverso de to_dict)."""
        data = dict(data)
        for key in ("created_at", "updated_at"):
            if isinstance(data.get(key), str):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)

    def __str__(self) -> str:
        return (
            f"[{self.id[:8]}] {self.title} "
            f"({self.ticket_type.value}, {self.priority.value}, {self.status.value})"
        )