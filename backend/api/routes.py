from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.facade import BackendFacade

router = APIRouter()
facade = BackendFacade()

class TicketRequest(BaseModel):
    texto: str

class MoveTicketRequest(BaseModel):
    ticket_id: int
    estado_actual: str
    nuevo_estado: str

@router.post("/classify")
def classify_ticket_endpoint(ticket: TicketRequest):
    if not ticket.texto or len(ticket.texto.strip()) < 5:
        raise HTTPException(status_code=400, detail="Texto demasiado corto o vacío para clasificar")

    # Usamos directamente la fachada unificada
    return facade.process_and_create_ticket(ticket.texto)

@router.post("/move-ticket")
def move_ticket_endpoint(data: MoveTicketRequest):
    try:
        # Transición segura usando el Workflow a través de la fachada
        return facade.move_ticket(data.ticket_id, data.estado_actual, data.nuevo_estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tickets")
def get_all_tickets_endpoint():
    return {
        "status": "ok",
        "tickets": []
    }