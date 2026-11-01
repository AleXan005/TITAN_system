// Configuración compartida. Es el único lugar que repite reglas del backend.
const { useState, useEffect } = React;

const API_URL = "/api/v1";

// Umbral de ConfidenceRule en services/rules_engine.py
const UMBRAL_CONFIANZA = 35;

// Categorías de database/init.sql
const CATEGORIAS = ["Soporte Técnico", "Redes", "Accesos", "Facturación"];

// Estados y transiciones de services/workflow.py
const ESTADOS = {
  NUEVO: "Nuevo",
  REVISION: "En revisión",
  EN_PROGRESO: "En progreso",
  RESOLVIDO: "Resuelto",
  CERRADO: "Cerrado",
};
const TRANSICIONES = {
  NUEVO: ["REVISION", "EN_PROGRESO"],
  REVISION: ["EN_PROGRESO", "CERRADO"],
  EN_PROGRESO: ["RESOLVIDO"],
  RESOLVIDO: ["CERRADO", "EN_PROGRESO"],
  CERRADO: [],
};


const AGENTES = [];
