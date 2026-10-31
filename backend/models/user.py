"""Modelo de dominio `User`.

Responsabilidad: representar a una persona del equipo y validar sus datos.
NO sabe de bases de datos ni de asignación automática (eso es de
`services/assignment_service.py`, Dev B).
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from models.enums import UserRole
from models.exceptions import ValidationError

NAME_MAX_LENGTH = 80
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _now() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


@dataclass
class User:
    """Usuario de la aplicación (miembro del equipo)."""

    name: str
    email: str
    role: UserRole = UserRole.DESARROLLADOR
    active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=_now)

    # ------------------------------------------------------------------
    # Inicialización y validación
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        self.name = self._clean_name(self.name)
        self.email = self._clean_email(self.email)
        self.role = self._to_role(self.role)

    @staticmethod
    def _clean_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("El nombre del usuario no puede estar vacío.")
        name = name.strip()
        if len(name) > NAME_MAX_LENGTH:
            raise ValidationError(
                f"El nombre no puede superar {NAME_MAX_LENGTH} caracteres."
            )
        return name

    @staticmethod
    def _clean_email(email: str) -> str:
        if not isinstance(email, str) or not _EMAIL_PATTERN.match(email.strip()):
            raise ValidationError(f"Correo electrónico inválido: '{email}'.")
        return email.strip().lower()

    @staticmethod
    def _to_role(role: Any) -> UserRole:
        if isinstance(role, UserRole):
            return role
        try:
            return UserRole(role)
        except ValueError:
            valid = ", ".join(r.value for r in UserRole)
            raise ValidationError(
                f"Rol inválido: '{role}'. Opciones: {valid}."
            ) from None

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def update_profile(
        self, name: Optional[str] = None, email: Optional[str] = None
    ) -> None:
        """Edita nombre y/o correo."""
        if name is not None:
            self.name = self._clean_name(name)
        if email is not None:
            self.email = self._clean_email(email)

    def change_role(self, new_role: UserRole | str) -> None:
        self.role = self._to_role(new_role)

    def deactivate(self) -> None:
        """Desactiva al usuario (no se borra para conservar el historial)."""
        self.active = False

    def activate(self) -> None:
        self.active = True

    # ------------------------------------------------------------------
    # Propiedades de consulta
    # ------------------------------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def can_be_assigned(self) -> bool:
        """Solo usuarios activos que no sean únicamente reportadores."""
        return self.active and self.role != UserRole.REPORTADOR

    # ------------------------------------------------------------------
    # Serialización (la usan storage/ y api/)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        data = dict(data)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)

    def __str__(self) -> str:
        estado = "activo" if self.active else "inactivo"
        return f"[{self.id[:8]}] {self.name} <{self.email}> ({self.role.value}, {estado})"