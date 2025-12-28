"""
Funções utilitárias de logging e helpers.
"""
import logging
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE

# Configurar logger
logger = logging.getLogger("bybit_bot")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Handler para arquivo
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(getattr(logging, LOG_LEVEL))

# Handler para console
ch = logging.StreamHandler()
ch.setLevel(getattr(logging, LOG_LEVEL))

# Formato
formatter = logging.Formatter(
    '[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

def log(msg: str, level: str = "info"):
    """Log com timestamp."""
    getattr(logger, level.lower())(msg)

def log_trade(side: str, qty, price, reason: str = ""):
    """Log de operação de trade."""
    log(f"TRADE: {side} {qty} @ {price} [{reason}]", "info")

def log_error(msg: str, exc: Exception = None):
    """Log de erro."""
    if exc:
        log(f"ERROR: {msg} - {exc}", "error")
    else:
        log(f"ERROR: {msg}", "error")
