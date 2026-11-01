function TicketForm({ enviando, error, onEnviar }) {
  const [texto, setTexto] = useState("");

  function enviar(e) {
    e.preventDefault();
    onEnviar(texto.trim());
  }

  return (
    <form onSubmit={enviar}>
      <label htmlFor="descripcion">Descripción de la incidencia</label>
      <textarea id="descripcion" rows={6} value={texto} onChange={(e) => setTexto(e.target.value)} />
      {error && <p className="error" role="alert">{error}</p>}
      <button type="submit" className="boton" disabled={enviando}>
        {enviando ? "Enviando…" : "Enviar"}
      </button>
    </form>
  );
}
