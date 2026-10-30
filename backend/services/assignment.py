class AssignmentService:
    def __init__(self, notifier=None):
        self.notifier = notifier

    def assign_automatically(self, ticket_id: int, categoria: str, agentes_disponibles: list[dict]) -> str:
        """
        Asigna el ticket al agente de la categoría con menor cantidad de tickets activos.
        agentes_disponibles = [{"id": "A1", "nombre": "Carlos", "carga": 3}, ...]
        """
        if not agentes_disponibles:
            return "SIN_AGENTE_DISPONIBLE"

        # Elegir el agente con menor carga de trabajo
        agente_optimo = min(agentes_disponibles, key=lambda x: x["carga"])
        
        if self.notifier:
            self.notifier.send(agente_optimo["nombre"], f"Se te asignó el Ticket #{ticket_id}.")

        return agente_optimo["id"]