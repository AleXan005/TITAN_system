function ReportPage({ onRegistrar }) {
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");

  async function enviar(texto) {
    setEnviando(true);
    setError("");
    try {
      const clasificado = await clasificarTicket(texto);
      setResultado(onRegistrar(clasificado));
    } catch (e) {
      setError(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section>
      <h1>Captura de ticket</h1>
      {resultado
        ? <ClassificationResult ticket={resultado} onNuevo={() => setResultado(null)} />
        : <TicketForm enviando={enviando} error={error} onEnviar={enviar} />}
    </section>
  );
}
