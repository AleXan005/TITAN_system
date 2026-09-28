from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import psycopg2

app = FastAPI(
    title="TITAN API - Ticket Intelligent Triage and Assignment Network",
    version="1.2"
)

# Cargar modelo de IA
MODEL_PATH = "classifier_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    "dbname": "titan_db",
    "user": "postgres",
    "password": "admin123",
    "host": "localhost",
    "port": "5432"
}

class TicketRequest(BaseModel):
    texto: str

def guardar_ticket_bd(texto: str, categoria: str, confianza: float):
    """Guarda el ticket clasificado directamente en PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            INSERT INTO tickets (texto_original, categoria_asignada, nivel_confianza)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (texto, categoria, confianza))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar en BD: {e}")
        return False

@app.get("/")
def read_root():
    return {"mensaje": "API de TITAN v1.2 conectada a PostgreSQL."}

@app.post("/classify")
def classify_ticket(ticket: TicketRequest):
    if not model:
        return {"error": "Modelo no encontrado."}
    
    # Inferencia de IA
    prediction = model.predict([ticket.texto])[0]
    probabilities = model.predict_proba([ticket.texto])[0]
    max_prob = round(float(max(probabilities)) * 100, 2)
    
    # Guardar en base de datos PostgreSQL
    guardado = guardar_ticket_bd(ticket.texto, prediction, max_prob)
    
    return {
        "texto_original": ticket.texto,
        "categoria_asignada": prediction,
        "porcentaje_confianza": f"{max_prob}%",
        "persistencia_bd": "Guardado exitosamente" if guardado else "Error al guardar",
        "estatus": "Clasificado exitosamente"
    }