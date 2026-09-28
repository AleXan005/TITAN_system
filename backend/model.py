import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Dataset Sintético de Prueba para TITAN
data = {
    'texto': [
        "No puedo entrar a mi correo corporativo contraseña bloqueada",
        "Olvidé mi clave de acceso al sistema de inventarios",
        "La impresora del departamento de finanzas no imprime y da error de red",
        "No hay internet en el tercer piso ni conexión por cable",
        "El servidor de la base de datos no responde a las peticiones",
        "Necesito el reembolso de la factura del servicio de internet",
        "Error en la plataforma de cobro y facturación mensual",
        "Solicito cambio de contraseña y desbloqueo de usuario"
    ],
    'categoria': [
        "Accesos",
        "Accesos",
        "Redes",
        "Redes",
        "Soporte Técnico",
        "Facturación",
        "Facturación",
        "Accesos"
    ]
}

df = pd.DataFrame(data)

# Pipeline de NLP: Limpieza, TF-IDF y Clasificador Supervisado
model = make_pipeline(
    TfidfVectorizer(stop_words=['de', 'el', 'la', 'en', 'del', 'no', 'a', 'y', 'los', 'las']),
    MultinomialNB()
)

print("Entrenando el modelo de TITAN...")
model.fit(df['texto'], df['categoria'])

# Guardar el archivo entrenado
joblib.dump(model, 'classifier_model.pkl')
print("¡Modelo entrenado exitosamente como 'classifier_model.pkl'!")