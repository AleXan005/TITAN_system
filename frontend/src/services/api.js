// Cliente HTTP único (fetch). Ningún componente llama a fetch directamente.
async function peticion(ruta, opciones = {}) {
  let res;
  try {
    res = await fetch(API_URL + ruta, {
      headers: { "Content-Type": "application/json" },
      ...opciones,
    });
  } catch {
    throw new Error("No se pudo conectar con el servidor.");
  }
  const datos = await res.json().catch(() => null);
  if (!res.ok) {
    const detalle = datos && datos.detail;
    throw new Error(typeof detalle === "string" ? detalle : "El servidor no pudo procesar la solicitud.");
  }
  return datos;
}
