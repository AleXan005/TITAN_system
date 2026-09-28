from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

app = FastAPI(
    title="TITAN API - Ticket Intelligent Triage and Assignment Network",
    version="1.0"
)

MODEL_PATH = "classifier_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

class TicketRequest(BaseModel):
    texto: str

@app.get("/")
def read_root():
    return {"mensaje": "API de TITAN operativa."}

@app.post("/classify")
def classify_ticket(ticket: TicketRequest):
    if not model:
        return {"error": "Modelo no encontrado."}
    
    prediction = model.predict([ticket.texto])[0]
    return {
        "texto_original": ticket.texto,
        "categoria_asignada": prediction,
        "estatus": "Clasificado exitosamente"
    }