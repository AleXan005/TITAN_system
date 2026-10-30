from services.rules_engine import RulesEngine, PriorityKeywordsRule, ConfidenceRule

def test_regla_prioridad_alta():
    rule = PriorityKeywordsRule()
    res = rule.evaluate({"texto": "falla critica en el servidor"})
    assert res["triggered"] is True
    assert res["prioridad"] == "ALTA"

def test_regla_confianza_baja():
    rule = ConfidenceRule(umbral=35.0)
    res = rule.evaluate({"confianza": 20.0})
    assert res["triggered"] is True
    assert res["estado_asignacion"] == "REVISION_MANUAL"

def test_motor_de_reglas_completo():
    engine = RulesEngine()
    res = engine.process({"texto": "solicitud comun", "confianza": 80.0})
    assert res["prioridad"] == "BAJA"
    assert res["estado_asignacion"] == "ASIGNADO_AUTOMATICO"