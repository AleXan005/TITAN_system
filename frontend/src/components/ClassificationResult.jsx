function ClassificationResult({ ticket, onNuevo }) {
  return (
    <section className="resultado" aria-live="polite">
      <h2>Ticket #{ticket.id} registrado</h2>
      <dl>
        <dt>Categoría</dt>
        <dd>{ticket.categoria}</dd>
        <dt>Nivel de confianza</dt>
        <dd>{ticket.confianza} %</dd>
      </dl>
      <button className="boton boton--claro" onClick={onNuevo}>Nueva incidencia</button>
    </section>
  );
}
