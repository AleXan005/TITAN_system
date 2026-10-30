from abc import ABC, abstractmethod

class Rule(ABC):
    """Clase base abstracta para cualquier regla del sistema."""
    @abstractmethod
    def evaluate(self, ticket_data: dict) -> dict:
        pass


class ConfidenceRule(Rule):
    """Regla que evalúa si la confianza de la IA es suficiente."""
    def __init__(self, umbral: float = 35.0):
        self.umbral = umbral

    def evaluate(self, ticket_data: dict) -> dict:
        confianza = ticket_data.get("confianza", 0.0)
        if confianza < self.umbral:
            return {
                "triggered": True,
                "estado_asignacion": "REVISION_MANUAL",
                "motivo": f"Confianza de IA ({confianza}%) menor al umbral ({self.umbral}%)."
            }
        return {"triggered": False, "estado_asignacion": "ASIGNADO_AUTOMATICO"}


class PriorityKeywordsRule(Rule):
    """Regla que detecta palabras clave urgentes en el texto."""
    KEYWORDS = ["urgente", "servidor", "caido", "caído", "caida", "caída", "bloqueado", "falla critica"]

    def evaluate(self, ticket_data: dict) -> dict:
        texto = ticket_data.get("texto", "").lower()
        if any(kw in texto for kw in self.KEYWORDS):
            return {"triggered": True, "prioridad": "ALTA", "motivo": "Palabra clave crítica detectada."}
        return {"triggered": False, "prioridad": "MEDIA"}


class RulesEngine:
    """Ejecuta una colección de reglas en orden."""
    def __init__(self):
        self.rules: list[Rule] = [
            PriorityKeywordsRule(),
            ConfidenceRule(umbral=35.0)
        ]

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def process(self, ticket_data: dict) -> dict:
        result = {
            "estado_asignacion": "ASIGNADO_AUTOMATICO",
            "prioridad": "BAJA",
            "motivos": []
        }
        for rule in self.rules:
            eval_res = rule.evaluate(ticket_data)
            if eval_res.get("triggered"):
                if "estado_asignacion" in eval_res:
                    result["estado_asignacion"] = eval_res["estado_asignacion"]
                if "prioridad" in eval_res:
                    result["prioridad"] = eval_res["prioridad"]
                result["motivos"].append(eval_res.get("motivo"))
        return result