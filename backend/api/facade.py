from services.ml_service import MLService
from services.rules_engine import RulesEngine
from services.workflow import WorkflowManager, TicketState
from services.notifier import ConsoleNotifier
from services.assignment import AssignmentService

class BackendFacade:
    def __init__(self, repo=None):
        self.repo = repo
        self.ml_service = MLService()
        self.rules_engine = RulesEngine()
        self.notifier = ConsoleNotifier()
        self.assignment_service = AssignmentService(notifier=self.notifier)

    def process_and_create_ticket(self, texto: str) -> dict:
        """Método principal usado por el frontend para procesar un nuevo ticket."""
        # 1. Inferencia de IA
        ml_res = self.ml_service.predict_ticket(texto)
        
        # 2. Evaluación con el Motor de Reglas
        ticket_payload = {"texto": texto, "confianza": ml_res["confianza"]}
        rules_res = self.rules_engine.process(ticket_payload)

        # 3. Estado inicial usando Workflow
        estado_inicial = TicketState.REVISION if rules_res["estado_asignacion"] == "REVISION_MANUAL" else TicketState.NUEVO

        ticket_creado = {
            "texto_original": texto,
            "categoria": ml_res["categoria"],
            "confianza": ml_res["confianza"],
            "prioridad": rules_res["prioridad"],
            "estado": estado_inicial,
            "motivos_reglas": rules_res["motivos"]
        }

        # 4. Notificar
        self.notifier.send("Soporte_Admin", f"Nuevo ticket creado con estado {estado_inicial}")

        return ticket_creado

    def move_ticket(self, ticket_id: int, current_state: str, new_state: str) -> dict:
        """Transición de estado segura usando el WorkflowManager."""
        estado_nuevo = WorkflowManager.validate_and_transition(current_state, new_state)
        return {"ticket_id": ticket_id, "nuevo_estado": estado_nuevo, "status": "Transición exitosa"}