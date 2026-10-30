import pytest
from services.workflow import WorkflowManager, TicketState
from services.rules_engine import RulesEngine

def test_transicion_workflow_valida():
    nuevo_estado = WorkflowManager.validate_and_transition(TicketState.NUEVO, TicketState.EN_PROGRESO)
    assert nuevo_estado == TicketState.EN_PROGRESO

def test_transicion_workflow_invalida():
    with pytest.raises(ValueError):
        WorkflowManager.validate_and_transition(TicketState.NUEVO, TicketState.CERRADO)

def test_motor_de_reglas_alta_prioridad():
    engine = RulesEngine()
    res = engine.process({"texto": "El servidor está caído urgente", "confianza": 80.0})
    assert res["prioridad"] == "ALTA"