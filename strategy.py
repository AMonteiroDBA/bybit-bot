"""
Estrátgia de crossover de médias móveis simples.
Short MA cruza acima Long MA = BUY
Short MA cruza abaixo Long MA = SELL
"""
from decimal import Decimal
from typing import List, Optional
from config import SHORT_MA_WINDOW, LONG_MA_WINDOW, TAKE_PROFIT_PCT, STOP_LOSS_PCT
from utils import log

class Position:
    """Representa uma posição aberta."""
    def __init__(self, side: str, entry_price: Decimal, qty: Decimal):
        self.side = side  # "long"
        self.entry_price = entry_price
        self.qty = qty
        self.entry_time = None

class MovingAverageStrategy:
    """Estratégia de crossover de médias móveis."""
    
    def __init__(self, short_window: int = SHORT_MA_WINDOW,
                 long_window: int = LONG_MA_WINDOW,
                 tp_pct: Decimal = TAKE_PROFIT_PCT,
                 sl_pct: Decimal = STOP_LOSS_PCT):
        self.short_window = short_window
        self.long_window = long_window
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.position: Optional[Position] = None
        self.ma_short_prev = Decimal("0")
        self.ma_long_prev = Decimal("0")

    @staticmethod
    def _calculate_ma(prices: List[Decimal], window: int) -> Decimal:
        """Calcula média móvel simples."""
        if len(prices) < window:
            return Decimal("0")
        subset = prices[-window:]
        return sum(subset) / Decimal(len(subset))

    def update(self, closes: List[Decimal]) -> str:
        """Atualiza estado e retorna sinal ('buy', 'sell', 'hold')."""
        if len(closes) < self.long_window + 1:
            return "hold"

        ma_short = self._calculate_ma(closes, self.short_window)
        ma_long = self._calculate_ma(closes, self.long_window)

        signal = "hold"

        if self.position is None:
            if (self.ma_short_prev <= self.ma_long_prev and ma_short > ma_long):
                signal = "buy"
                log(f"BUY signal: MA{self.short_window} ({ma_short}) > MA{self.long_window} ({ma_long})")
        else:
            if (self.ma_short_prev >= self.ma_long_prev and ma_short < ma_long):
                signal = "sell"
                log(f"SELL signal: MA{self.short_window} ({ma_short}) < MA{self.long_window} ({ma_long})")

        self.ma_short_prev = ma_short
        self.ma_long_prev = ma_long
        return signal

    def check_exit(self, last_price: Decimal) -> str:
        """Verifica take-profit ou stop-loss."""
        if self.position is None:
            return "hold"

        entry = self.position.entry_price
        change = (last_price - entry) / entry

        if change >= self.tp_pct:
            log(f"Take profit atingido: {change:.4%}")
            return "sell"
        if change <= -self.sl_pct:
            log(f"Stop loss atingido: {change:.4%}")
            return "sell"
        return "hold"

    def on_buy(self, price: Decimal, qty: Decimal):
        """Registra entrada de posição longa."""
        self.position = Position("long", price, qty)
        log(f"Position opened: LONG {qty} @ {price}")

    def on_sell(self, price: Decimal):
        """Registra saída de posição."""
        if self.position:
            pnl = (price - self.position.entry_price) * self.position.qty
            pnl_pct = ((price - self.position.entry_price) / self.position.entry_price) * 100
            log(f"Position closed: EXIT @ {price}, PnL: {pnl:.2f} USDT ({pnl_pct:.2f}%)")
            self.position = None
