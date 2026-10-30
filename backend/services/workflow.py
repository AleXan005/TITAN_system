class TicketState:
    NUEVO = "NUEVO"
    REVISION = "REVISION"
    EN_PROGRESO = "EN_PROGRESO"
    RESOLVIDO = "RESOLVIDO"
    CERRADO = "CERRADO"

class WorkflowManager:
    # Definición estricta de transiciones válidas
    TRANSICIONES_VALIDAS = {
        TicketState.NUEVO: [TicketState.REVISION, TicketState.EN_PROGRESO],
        TicketState.REVISION: [TicketState.EN_PROGRESO, TicketState.CERRADO],
        TicketState.EN_PROGRESO: [TicketState.RESOLVIDO],
        TicketState.RESOLVIDO: [TicketState.CERRADO, TicketState.EN_PROGRESO],
        TicketState.CERRADO: []
    }

    @classmethod
    def can_transition(cls, current_state: str, new_state: str) -> bool:
        allowed = cls.TRANSICIONES_VALIDAS.get(current_state, [])
        return new_state in allowed

    @classmethod
    def validate_and_transition(cls, current_state: str, new_state: str) -> str:
        if not cls.can_transition(current_state, new_state):
            raise ValueError(f"Transición no permitida de '{current_state}' a '{new_state}'.")
        return new_state