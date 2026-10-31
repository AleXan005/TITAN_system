"""Logging central de la aplicación.

Todos los módulos obtienen su logger con `get_logger(__name__)`. Así cada
mensaje indica de qué módulo viene, y localizar un fallo es leer una línea:

    2026-10-31 15:08:01 | ERROR | ticket_automator.storage.database | ...

Llama a `setup_logging(settings)` UNA vez al arrancar la aplicación. Si no se
llama, los módulos no imprimen nada (comportamiento normal de una librería).
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import Settings

ROOT_LOGGER_NAME = "ticket_automator"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_NAME = "ticket_automator.log"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 3

# Sin setup_logging() no se imprime nada ni aparece el aviso de "no handlers".
logging.getLogger(ROOT_LOGGER_NAME).addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """Devuelve el logger de un módulo. Uso: `log = get_logger(__name__)`."""
    if name == ROOT_LOGGER_NAME or name.startswith(ROOT_LOGGER_NAME + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")


def setup_logging(settings: Settings) -> logging.Logger:
    """Configura consola y/o archivo según los ajustes. Es seguro llamarla
    varias veces: reemplaza los handlers anteriores en lugar de duplicarlos."""
    root = logging.getLogger(ROOT_LOGGER_NAME)
    root.setLevel(settings.log_level)
    root.propagate = False

    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    if settings.log_to_console:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    if settings.log_to_file:
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / LOG_FILE_NAME,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    if not root.handlers:
        root.addHandler(logging.NullHandler())

    return root
