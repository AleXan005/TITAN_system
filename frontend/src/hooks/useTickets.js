// Estado de la lista de tickets. Como el backend aún no guarda ni devuelve el historial,
// se respalda en localStorage hasta que GET /tickets funcione.
const CLAVE = "titan.tickets";

function leerGuardados() {
  try { return JSON.parse(localStorage.getItem(CLAVE)) || []; } catch { return []; }
}

function useTickets() {
  const [tickets, setTickets] = useState(leerGuardados);

  useEffect(() => {
    try { localStorage.setItem(CLAVE, JSON.stringify(tickets)); } catch {}
  }, [tickets]);

  useEffect(() => {
    listarTickets()
      .then((remotos) => setTickets((actuales) => {
        const ids = new Set(actuales.map((t) => t.id));
        return [...actuales, ...remotos.filter((t) => !ids.has(t.id))];
      }))
      .catch(() => {});
  }, []);

  function registrar(ticket) {
    const id = ticket.id ?? Math.max(0, ...tickets.map((t) => t.id)) + 1;
    const nuevo = { ...ticket, id };
    setTickets([nuevo, ...tickets]);
    return nuevo;
  }

  function actualizar(id, cambios) {
    setTickets(tickets.map((t) => (t.id === id ? { ...t, ...cambios } : t)));
  }

  // Asignación: sin endpoint en el backend todavía, solo se guarda en el front.
  function asignar(id, agenteId) {
    actualizar(id, { asignadoA: agenteId || null });
  }

  async function cambiarEstado(ticket, nuevoEstado) {
    await moverTicket(ticket.id, ticket.estado, nuevoEstado);
    actualizar(ticket.id, { estado: nuevoEstado });
  }

  return { tickets, registrar, asignar, cambiarEstado };
}
