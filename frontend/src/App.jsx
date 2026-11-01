function App() {
  const [vista, setVista] = useState("reporte");
  const { tickets, registrar, asignar, cambiarEstado } = useTickets();

  return (
    <>
      <Header vista={vista} onCambiar={setVista} />
      <main>
        {vista === "reporte"
          ? <ReportPage onRegistrar={registrar} />
          : <DashboardPage tickets={tickets} onAsignar={asignar} onCambiarEstado={cambiarEstado} />}
      </main>
    </>
  );
}
