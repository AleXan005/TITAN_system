from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass

class ConsoleNotifier(Notifier):
    """Implementación simple para desarrollo e impresiones por consola."""
    def send(self, recipient: str, message: str) -> bool:
        print(f"🔔 [NOTIFICACIÓN a {recipient}]: {message}")
        return True

class EmailNotifier(Notifier):
    """Estructura preparada para integración futura con servidor SMTP."""
    def send(self, recipient: str, message: str) -> bool:
        # Lógica de envío simulada o SMTP
        print(f"📧 [EMAIL SIMULADO a {recipient}]: {message}")
        return True