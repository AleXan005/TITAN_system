"""Execepcciones de la aplicacion"""


class TicketAutomatorError(Exception):
    """Clase base de todos los errores de la aplicación."""


class ValidationError(TicketAutomatorError):
    """Un dato del modelo no cumple las reglas de validación."""


class TicketNotFoundError(TicketAutomatorError):
    """No existe un ticket con el id solicitado."""

    def __init__(self, ticket_id: str):
        super().__init__(f"No se encontró el ticket '{ticket_id}'.")
        self.ticket_id = ticket_id


class InvalidTransitionError(TicketAutomatorError):
    """Se intentó una transición de estado no permitida (la lanza Dev B)."""

    def __init__(self, current: str, target: str):
        super().__init__(f"Transición no permitida: '{current}' -> '{target}'.")
        self.current = current
        self.target = target


class RepositoryError(TicketAutomatorError):
    """Falló una operación de persistencia."""


class DuplicateError(RepositoryError):
    """Ya existe un registro con ese valor único (id, correo o clave)."""


class UserNotFoundError(TicketAutomatorError):
    """No existe un usuario con el dato solicitado."""

    def __init__(self, identifier: str):
        super().__init__(f"No se encontró el usuario '{identifier}'.")
        self.identifier = identifier


class ProjectNotFoundError(TicketAutomatorError):
    """No existe un proyecto con el dato solicitado."""

    def __init__(self, identifier: str):
        super().__init__(f"No se encontró el proyecto '{identifier}'.")
        self.identifier = identifier


class ConfigError(TicketAutomatorError):
    """La configuración de la aplicación es inválida o no se pudo leer."""
