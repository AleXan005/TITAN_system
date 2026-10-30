import pytest
from services.workflow import WorkflowManager, TicketState

def test_can_transition_exitoso():
    assert WorkflowManager.can_transition(TicketState.NUEVO, TicketState.EN_PROGRESO) is True

def test_can_transition_fallido():
    assert WorkflowManager.can_transition(TicketState.NUEVO, TicketState.CERRADO) is False

def test_validate_and_transition_excepcion():
    with pytest.raises(ValueError):
        WorkflowManager.validate_and_transition(TicketState.CERRADO, TicketState.EN_PROGRESO)