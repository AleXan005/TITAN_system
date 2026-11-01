function TicketTable({ tickets, onAsignar, onCambiarEstado }) {
  const [error, setError] = useState("");

  async function mover(ticket, nuevo) {
    setError("");
    try { await onCambiarEstado(ticket, nuevo); } catch (e) { setError(e.message); }
  }

  return (
    <>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="tabla-marco">
      <table>
        <thead>
          <tr>
            <th>#</th><th>Descripción</th><th>Categoría</th><th>Confianza</th>
            <th>Prioridad</th><th>Estado</th><th>Asignado a</th>
          </tr>
        </thead>
        <tbody>
          {tickets.length === 0 && (
            <tr><td colSpan={7} className="tabla__vacia">No hay tickets.</td></tr>
          )}
          {tickets.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td className="tabla__texto">{t.texto}</td>
              <td>{t.categoria}</td>
              <td>{t.confianza} %</td>
              <td>{t.prioridad}</td>
              <td>
                <select value={t.estado} aria-label={`Estado del ticket ${t.id}`}
                  onChange={(e) => mover(t, e.target.value)}>
                  <option value={t.estado}>{ESTADOS[t.estado] || t.estado}</option>
                  {(TRANSICIONES[t.estado] || []).map((s) => <option key={s} value={s}>{ESTADOS[s]}</option>)}
                </select>
              </td>
              <td>
                <select value={t.asignadoA || ""} aria-label={`Asignar ticket ${t.id}`}
                  onChange={(e) => onAsignar(t.id, e.target.value)}>
                  <option value="">Sin asignar</option>
                  {AGENTES.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </>
  );
}
