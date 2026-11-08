from models.ticket import Ticket
from services.assignment import AssignmentService
from services.ml_service import MLService
from services.notifier import ConsoleNotifier
from services.rules_engine import RulesEngine
from services.workflow import TicketState, WorkflowManager
from storage.factory import create_sqlite_storage


class BackendFacade:

  def __init__(self, db_path: str = "data/tickets.db"):
    self.storage = create_sqlite_storage(db_path)
    self.ml_service = MLService()
    self.rules_engine = RulesEngine()
    self.notifier = ConsoleNotifier()
    self.assignment_service = AssignmentService(notifier=self.notifier)

  def process_and_create_ticket(self, texto: str) -> dict:
    """Procesa el ticket con IA + Reglas y lo guarda en la base de datos."""
    # 1. Inferencia de IA
    ml_res = self.ml_service.predict_ticket(texto)

    # 2. Evaluación con el Motor de Reglas
    ticket_payload = {"texto": texto, "confianza": ml_res["confianza"]}
    rules_res = self.rules_engine.process(ticket_payload)

    # 3. Estado inicial usando Workflow
    estado_inicial = (
        TicketState.REVISION
        if rules_res["estado_asignacion"] == "REVISION_MANUAL"
        else TicketState.NUEVO
    )

    # 4. Crear el modelo de Dominio (modelo Ticket de Adrián)
    # Truncamos el título a 100 caracteres por la regla de validación de Ticket
    titulo_limpio = texto[:100] if len(texto) > 100 else texto

    nuevo_ticket = Ticket(
        title=titulo_limpio,
        description=texto,
        priority=rules_res["prioridad"].lower(),  # "alta", "media", "baja"
        status=estado_inicial.lower(),
        labels=[ml_res["categoria"]],
    )

    # 5. Guardar en SQLite a través del repositorio de Adrián
    self.storage.tickets.add(nuevo_ticket)

    # 6. Notificar
    self.notifier.send(
        "Soporte_Admin", f"Nuevo ticket creado con ID {nuevo_ticket.id}"
    )

    # 7. Retornar diccionario para el frontend
    res_dict = nuevo_ticket.to_dict()
    res_dict["categoria"] = ml_res["categoria"]
    res_dict["confianza"] = ml_res["confianza"]
    res_dict["motivos_reglas"] = rules_res["motivos"]
    return res_dict

  def list_tickets(self) -> list[dict]:
    """Devuelve los tickets persistidos en formato serializable."""
    return [ticket.to_dict() for ticket in self.storage.tickets.list_all()]

  def move_ticket(
      self, ticket_id: str, current_state: str, new_state: str
  ) -> dict:
    """Transición de estado con Workflow y persistencia."""
    estado_actual = current_state.upper()
    estado_objetivo = new_state.upper()
    estado_nuevo = WorkflowManager.validate_and_transition(
        estado_actual, estado_objetivo
    )

    # Si el ticket existe en BD, actualizamos su estado
    ticket = self.storage.tickets.get(ticket_id)
    estado_dominio = "hecho" if estado_nuevo == "RESOLVIDO" else estado_nuevo.lower()
    ticket.change_status(estado_dominio)
    self.storage.tickets.update(ticket)

    return {
        "ticket_id": ticket_id,
        "nuevo_estado": estado_nuevo,
        "status": "Transición exitosa",
    }
