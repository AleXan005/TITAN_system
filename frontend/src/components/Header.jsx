function Header({ vista, onCambiar }) {
  return (
    <header className="cabecera">
      <span className="cabecera__marca">TITAN</span>
      <nav className="cabecera__nav">
        <button className={vista === "reporte" ? "activa" : ""} onClick={() => onCambiar("reporte")}>
          Captura de ticket
        </button>
        <button className={vista === "panel" ? "activa" : ""} onClick={() => onCambiar("panel")}>
          Panel de soporte
        </button>
      </nav>
    </header>
  );
}
