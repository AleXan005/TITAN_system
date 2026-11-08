// La API devuelve nombres propios del backend; la UI usa siempre este modelo.
// Acepta `confianza` (lo que devuelve hoy) y `nivel_confianza` (nombre del Sprint II).
function normalizarTicket(raw, id) {
  const estado = String(raw.status ?? raw.estado ?? "nuevo").toLowerCase();
  const estadosUI = {
    nuevo: "NUEVO",
    revision: "REVISION",
    en_progreso: "EN_PROGRESO",
    hecho: "RESOLVIDO",
    cerrado: "CERRADO",
  };
  return {
    id: raw.id ?? id,
    texto: raw.description ?? raw.texto_original ?? "",
    categoria: raw.categoria ?? raw.categoria_asignada ?? raw.labels?.[0] ?? "Sin Clasificar",
    confianza: Number(raw.nivel_confianza ?? raw.confianza ?? 0),
    prioridad: raw.priority ?? raw.prioridad ?? "",
    estado: estadosUI[estado] ?? "NUEVO",
    asignadoA: raw.assignee_id ?? raw.agente_id ?? null,
  };
}

// POST /classify { texto }
async function clasificarTicket(texto) {
  const datos = await peticion("/classify", { method: "POST", body: JSON.stringify({ texto }) });
  return normalizarTicket(datos);
}

// GET /tickets  (hoy devuelve una lista vacía)
async function listarTickets() {
  const datos = await peticion("/tickets");
  return (datos.tickets || []).map((t) => normalizarTicket(t));
}

// POST /move-ticket { ticket_id, estado_actual, nuevo_estado }
function moverTicket(id, estadoActual, nuevoEstado) {
  return peticion("/move-ticket", {
    method: "POST",
    body: JSON.stringify({ ticket_id: id, estado_actual: estadoActual, nuevo_estado: nuevoEstado }),
  });
}
