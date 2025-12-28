"""
Configuração centralizada do bot.
Lê variáveis de ambiente do arquivo .env
"""
import os
from dotenv import load_dotenv
from decimal import Decimal

# Carrega .env
load_dotenv()

# ============ Credenciais Bybit ============
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api-testnet.bybit.com")

# ============ Trading Config ============
CATEGORY = os.getenv("BYBIT_CATEGORY", "spot")
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")

# ============ Risk Management ============
RISK_PER_TRADE = Decimal(os.getenv("RISK_PER_TRADE", "0.01"))
MAX_DAILY_LOSS = Decimal(os.getenv("MAX_DAILY_LOSS", "0.03"))
MIN_NOTIONAL = Decimal(os.getenv("MIN_NOTIONAL", "10"))
ACCOUNT_EQUITY = Decimal("400")

# ============ Strategy Parameters ============
SHORT_MA_WINDOW = int(os.getenv("SHORT_MA_WINDOW", "9"))
LONG_MA_WINDOW = int(os.getenv("LONG_MA_WINDOW", "21"))
TAKE_PROFIT_PCT = Decimal(os.getenv("TAKE_PROFIT_PCT", "0.02"))
STOP_LOSS_PCT = Decimal(os.getenv("STOP_LOSS_PCT", "0.01"))

# ============ Logging ============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# ============ Validação ============
if not API_KEY or not API_SECRET:
    raise ValueError("BYBIT_API_KEY e BYBIT_API_SECRET não configuradas no .env!")
