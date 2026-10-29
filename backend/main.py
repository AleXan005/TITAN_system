from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(
    title="TITAN API - Ticket Intelligent Triage and Assignment Network",
    version="2.0",
    description="API Modular para clasificación y gestión inteligente de tickets de soporte."
)

# Incluimos las rutas modulares de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "mensaje": "API de TITAN v2.0 Operativa",
        "documentacion": "/docs",
        "estado": "En ejecución"
    }