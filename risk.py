"""
Gestão de risco do bot de trading.
"""
from decimal import Decimal
from config import RISK_PER_TRADE, MAX_DAILY_LOSS, ACCOUNT_EQUITY, MIN_NOTIONAL
from utils import log, log_error

class RiskManager:
    """Gerencia exposição de risco e limites do bot."""
    
    def __init__(self):
        self.equity_base = ACCOUNT_EQUITY
        self.daily_pnl = Decimal("0")

    def can_trade(self) -> bool:
        """Verifica se pode fazer trade (não atingiu limite de perda diária)."""
        loss_limit = -self.equity_base * MAX_DAILY_LOSS
        if self.daily_pnl <= loss_limit:
            log(f"Limite de perda diária atingido: {self.daily_pnl} <= {loss_limit}")
            return False
        return True

    def update_pnl(self, realized_pnl: Decimal):
        """Atualiza PnL realizado do dia."""
        self.daily_pnl += realized_pnl
        log(f"Atualizando PnL diário para {self.daily_pnl}")

    def calc_position_size(self, price: Decimal) -> Decimal:
        """Calcula tamanho de posição baseado em risco.
        
        Retorna quantidade em moeda (ex. BTC), baseado em RISK_PER_TRADE%.
        """
        capital_risco = self.equity_base * RISK_PER_TRADE
        if capital_risco < MIN_NOTIONAL:
            capital_risco = MIN_NOTIONAL
        qty = capital_risco / price
        return qty.quantize(Decimal("0.0001"))

    def reset_daily_pnl(self):
        """Reseta PnL diário (chamar no fimção do dia)."""
        self.daily_pnl = Decimal("0")
        log("PnL diário resetado para 0")
