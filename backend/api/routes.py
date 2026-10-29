from fastapi import APIRouter
from pydantic import BaseModel
from services.ml_service import MLService
from services.rules_engine import RulesEngine

router = APIRouter()
ml_service = MLService()

class TicketRequest(BaseModel):
    texto: str

@router.post("/classify")
def classify_ticket_endpoint(ticket: TicketRequest):
    """
    Ruta urgente para Luis (Frontend) y Adrian (BD).
    Recibe el texto, lo evalúa con IA y devuelve el resultado.
    """
    # 1. Evaluamos con la IA
    ml_result = ml_service.predict_ticket(ticket.texto)
    
    # 2. Aplicamos reglas de negocio (confianza)
    evaluation = RulesEngine.evaluate_ticket(ml_result)
    
    return {
        "texto_original": ticket.texto,
        "categoria_asignada": evaluation["categoria_sugerida"],
        "nivel_confianza": evaluation["nivel_confianza"],
        "estado_asignacion": evaluation["estado_asignacion"],
        "mensaje": evaluation["regla_aplicada"]
    }

@router.get("/tickets")
def get_all_tickets_endpoint():
    """
    Ruta de lectura para que el Frontend muestre la lista de tickets.
    """
    # Nota: Aquí Adrian conectará su función de ticket_repo.py
    return {
        "status": "ok",
        "tickets": []
    }