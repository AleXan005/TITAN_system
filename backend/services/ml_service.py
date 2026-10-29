import joblib
import os

class MLService:
    def __init__(self, model_path: str = "classifier_model.pkl"):
        self.model_path = model_path
        self.model = joblib.load(model_path) if os.path.exists(model_path) else None

    def predict_ticket(self, texto: str) -> dict:
        if not self.model:
            return {"categoria": "Sin Clasificar", "confianza": 0.0}
        
        categoria = self.model.predict([texto])[0]
        probabilidades = self.model.predict_proba([texto])[0]
        confianza = round(float(max(probabilidades)) * 100, 2)

        return {
            "categoria": categoria,
            "confianza": confianza
        }