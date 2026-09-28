# 🚀 TITAN - Ticket Intelligent Triage and Assignment Network

**TITAN** es un sistema inteligente de clasificación y asignación automática de tickets de soporte técnico utilizando Procesamiento de Lenguaje Natural (NLP) y modelos de Aprendizaje Automático Supervisado.

## 🛠️ Stack Tecnológico
* **Backend:** Python 3.9+ / FastAPI
* **IA / NLP:** Scikit-Learn (TF-IDF + Multinomial Naive Bayes) / Pandas / Joblib
* **Base de Datos:** PostgreSQL
* **Control de Versiones:** Git & GitHub

## 📂 Estructura del Proyecto
```text
titan-project/
├── backend/
│   ├── main.py              # API REST (Endpoints)
│   ├── model.py             # Pipeline de entrenamiento de la IA
│   ├── requirements.txt     # Dependencias de Python
│   └── classifier_model.pkl # Modelo estadístico entrenado
├── database/
│   └── init.sql             # Scripts DDL/DML de PostgreSQL
├── .gitignore
└── README.md