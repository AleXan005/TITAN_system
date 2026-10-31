"""Archivo para enumerar los estados del ticket, prioridad y tipo"""

from enum import Enum


class Status(str, Enum):
    """clasificador de estatus del ticket"""
    
    NEW = "new"
    IN_PROGRES = "in_progres"
    CHECK = "check"
    FINISHED = "finished"


class Priority(str, Enum):
    """Prioridad del ticket"""

    LOW = "low"
    MID = "mid"
    TOP = "top"
    CIRTIC = "critic"


class ticketType (str, Enum):
    """Clasificador del tipo de ticket"""

    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"

class userRole(str, Enum):
    """Rol de cada usuario de la aplicacion"""

    ADMIN = "admin"
    DEVELOPER = "developer"
    REPORTER = "repoter"