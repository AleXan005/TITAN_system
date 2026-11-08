"""Archivo para enumerar los estados del ticket, prioridad y tipo"""

from enum import Enum

class Status(str, Enum):
    NUEVO = "nuevo"
    REVISION = "revision"
    EN_PROGRESO = "en_progreso"
    HECHO = "hecho"
    CERRADO = "cerrado"

class Priority(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class TicketType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TAREA = "tarea"

class UserRole(str, Enum):
    """Rol de cada usuario de la aplicación."""

    ADMIN = "admin"
    DESARROLLADOR = "desarrollador"
    REPORTADOR = "reportador"
    DEVELOPER = "desarrollador"
    REPORTER = "reportador"


# Alias para código que aún usa el nombre histórico.
userRole = UserRole
