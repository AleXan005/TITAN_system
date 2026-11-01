// Solo los dos filtros que piden los sprints: categoría y nivel de confianza.
function Filters({ filtros, onCambiar }) {
  return (
    <div className="filtros">
      <label>
        Categoría
        <select value={filtros.categoria} onChange={(e) => onCambiar({ ...filtros, categoria: e.target.value })}>
          <option value="">Todas</option>
          {CATEGORIAS.map((c) => <option key={c}>{c}</option>)}
        </select>
      </label>
      <label>
        Nivel de confianza
        <select value={filtros.confianza} onChange={(e) => onCambiar({ ...filtros, confianza: e.target.value })}>
          <option value="">Todos</option>
          <option value="baja">Menos de {UMBRAL_CONFIANZA} % (revisión manual)</option>
          <option value="suficiente">{UMBRAL_CONFIANZA} % o más</option>
        </select>
      </label>
    </div>
  );
}
