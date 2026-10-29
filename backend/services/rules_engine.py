class RulesEngine:
    UMBRAL_CONFIANZA = 60.0

    @classmethod
    def evaluate_ticket(cls, ml_result: dict) -> dict:
        confianza = ml_result.get("confianza", 0.0)
        categoria = ml_result.get("categoria", "Sin Clasificar")

        if confianza < cls.UMBRAL_CONFIANZA:
            estado_asignacion = "REVISION_MANUAL"
            mensaje = "Confianza baja: se requiere validación por un agente humano."
        else:
            estado_asignacion = "ASIGNADO_AUTOMATICO"
            mensaje = f"Ticket asignado automáticamente a la categoría {categoria}."

        return {
            "categoria_sugerida": categoria,
            "nivel_confianza": confianza,
            "estado_asignacion": estado_asignacion,
            "regla_aplicada": mensaje
        }