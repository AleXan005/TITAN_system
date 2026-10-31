"""Modelo de dominio `Project`.

Responsabilidad: representar un proyecto, su clave corta (por ejemplo "TIT")
y la lista de ids de sus miembros. Guarda ids, no objetos `User`, para que
los módulos sigan independientes entre sí.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from models.exceptions import ValidationError

NAME_MAX_LENGTH = 80
_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")


def _now() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


@dataclass
class Project:
    """Proyecto que agrupa tickets y miembros del equipo."""

    name: str
    key: str
    description: str = ""
    owner_id: Optional[str] = None
    member_ids: list[str] = field(default_factory=list)
    active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=_now)

    # ------------------------------------------------------------------
    # Inicialización y validación
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        self.name = self._clean_name(self.name)
        self.key = self._clean_key(self.key)
        self.description = (self.description or "").strip()
        self.member_ids = self._clean_members(self.member_ids)
        # El dueño siempre es miembro del proyecto.
        if self.owner_id and self.owner_id not in self.member_ids:
            self.member_ids.append(self.owner_id)

    @staticmethod
    def _clean_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("El nombre del proyecto no puede estar vacío.")
        name = name.strip()
        if len(name) > NAME_MAX_LENGTH:
            raise ValidationError(
                f"El nombre no puede superar {NAME_MAX_LENGTH} caracteres."
            )
        return name

    @staticmethod
    def _clean_key(key: str) -> str:
        key = str(key).strip().upper()
        if not _KEY_PATTERN.match(key):
            raise ValidationError(
                "La clave del proyecto debe tener de 2 a 10 caracteres, "
                "empezar con letra y usar solo letras o números (ej. 'TIT')."
            )
        return key

    @staticmethod
    def _clean_members(member_ids: list[str]) -> list[str]:
        cleaned: list[str] = []
        for member in member_ids or []:
            member = str(member).strip()
            if member and member not in cleaned:
                cleaned.append(member)
        return cleaned

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def update_details(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        """Edita nombre y/o descripción. La clave no se cambia una vez creada."""
        if name is not None:
            self.name = self._clean_name(name)
        if description is not None:
            self.description = description.strip()

    def add_member(self, user_id: str) -> None:
        user_id = str(user_id).strip()
        if not user_id:
            raise ValidationError("El id del miembro no puede estar vacío.")
        if user_id not in self.member_ids:
            self.member_ids.append(user_id)

    def remove_member(self, user_id: str) -> None:
        if user_id == self.owner_id:
            raise ValidationError(
                "No se puede quitar al dueño del proyecto; cambia el dueño primero."
            )
        if user_id in self.member_ids:
            self.member_ids.remove(user_id)

    def change_owner(self, user_id: str) -> None:
        """Cambia el dueño; el nuevo dueño pasa a ser miembro automáticamente."""
        self.add_member(user_id)
        self.owner_id = str(user_id).strip()

    def archive(self) -> None:
        self.active = False

    def reactivate(self) -> None:
        self.active = True

    # ------------------------------------------------------------------
    # Propiedades de consulta
    # ------------------------------------------------------------------
    def has_member(self, user_id: str) -> bool:
        return user_id in self.member_ids

    @property
    def member_count(self) -> int:
        return len(self.member_ids)

    # ------------------------------------------------------------------
    # Serialización (la usan storage/ y api/)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "key": self.key,
            "description": self.description,
            "owner_id": self.owner_id,
            "member_ids": list(self.member_ids),
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        data = dict(data)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)

    def __str__(self) -> str:
        estado = "activo" if self.active else "archivado"
        return f"[{self.key}] {self.name} ({self.member_count} miembros, {estado})"