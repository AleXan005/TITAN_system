// La API devuelve nombres propios del backend; la UI usa siempre este modelo.
// Acepta `confianza` (lo que devuelve hoy) y `nivel_confianza` (nombre del Sprint II).
function normalizarTicket(raw, id) {
  return {
    id: raw.id ?? id,
    texto: raw.texto_original ?? "",
    categoria: raw.categoria ?? raw.categoria_asignada ?? "Sin Clasificar",
    confianza: Number(raw.nivel_confianza ?? raw.confianza ?? 0),
    prioridad: raw.prioridad ?? "",
    estado: raw.estado ?? "NUEVO",
    asignadoA: raw.agente_id ?? null,
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
