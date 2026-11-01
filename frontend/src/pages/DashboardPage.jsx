function DashboardPage({ tickets, onAsignar, onCambiarEstado }) {
  const [filtros, setFiltros] = useState({ categoria: "", confianza: "" });

  const visibles = tickets.filter((t) =>
    (!filtros.categoria || t.categoria === filtros.categoria) &&
    (!filtros.confianza ||
      (filtros.confianza === "baja" ? t.confianza < UMBRAL_CONFIANZA : t.confianza >= UMBRAL_CONFIANZA))
  );

  return (
    <section>
      <h1>Panel de soporte</h1>
      <Filters filtros={filtros} onCambiar={setFiltros} />
      <TicketTable tickets={visibles} onAsignar={onAsignar} onCambiarEstado={onCambiarEstado} />
    </section>
  );
}
