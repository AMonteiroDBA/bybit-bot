"""
Loop principal do bot de trading Bybit.
Integra cliente, estratégia e gestão de risco.
"""
import time
from decimal import Decimal
from bybit_client import BybitClient
from strategy import MovingAverageStrategy
from risk import RiskManager
from utils import log, log_error, log_trade

def main():
    """Função principal do bot."""
    client = BybitClient()
    strategy = MovingAverageStrategy()
    risk = RiskManager()

    closes = []  # lista de últimos preços de fechamento

    log("Bot inicializado com sucesso")
    log(f"Estratégia: MA{strategy.short_window}/MA{strategy.long_window}")
    log(f"Stop Loss: {strategy.sl_pct*100:.1f}%, Take Profit: {strategy.tp_pct*100:.1f}%")
    log(f"Risco por trade: {risk.equity_base * Decimal('0.01')} USDT")

    while True:
        try:
            # Obter preço atual
            price = client.get_ticker()
            if price <= 0:
                log("Preço inválido, pulando iteração")
                time.sleep(5)
                continue

            closes.append(price)
            if len(closes) > 500:
                closes.pop(0)  # manter últimos 500 preços

            log(f"Preço atual: {price}")

            # Validar risco
            if not risk.can_trade():
                log("Trading desativado por limite de perda diária.")
                time.sleep(60)
                continue

            # Se há posição aberta, verifica exit (TP/SL)
            exit_signal = strategy.check_exit(price)
            if exit_signal == "sell" and strategy.position is not None:
                qty = strategy.position.qty
                resp = client.place_market_order("Sell", qty)
                if resp.get("retCode") == 0:
                    # Calcular PnL
                    pnl = (price - strategy.position.entry_price) * qty
                    pnl_pct = ((price - strategy.position.entry_price) / strategy.position.entry_price) * 100
                    risk.update_pnl(pnl)
                    log_trade("SELL", qty, price, f"PnL: {pnl_pct:.2f}%")
                    strategy.on_sell(price)
                else:
                    log_error(f"Falha ao fechar posição: {resp.get('retMsg')}")

            # Se sem posição, verifica sinal de entrada
            signal = strategy.update(closes)
            if signal == "buy" and strategy.position is None:
                qty = risk.calc_position_size(price)
                resp = client.place_market_order("Buy", qty)
                if resp.get("retCode") == 0:
                    log_trade("BUY", qty, price, "Nova posição")
                    strategy.on_buy(price, qty)
                else:
                    log_error(f"Falha ao abrir posição: {resp.get('retMsg')}")

            # Aguardar próxima iteração
            time.sleep(30)

        except KeyboardInterrupt:
            log("Bot interrompido pelo usuário.")
            break
        except Exception as e:
            log_error(f"Erro inesperado no loop principal", e)
            time.sleep(10)

    log("Bot encerrado.")

if __name__ == "__main__":
    main()
