"""
Cliente Bybit com autenticação HMAC SHA256 (API v5).
Spot only, sem alavancagem.
"""
import time
import json
import hmac
import hashlib
import requests
from typing import Dict, Any, List
from decimal import Decimal
from config import API_KEY, API_SECRET, BASE_URL, CATEGORY, SYMBOL
from utils import log, log_error

class BybitClient:
    """Cliente REST para Bybit API v5."""
    
    def __init__(self, api_key: str = API_KEY, api_secret: str = API_SECRET,
                 base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url.rstrip("/")
        self.recv_window = "5000"

    def _generate_signature(self, timestamp: str, method: str, endpoint: str,
                           params: Dict[str, Any]) -> str:
        """Gera assinatura HMAC SHA256 para Bybit v5."""
        if method == "GET":
            body_str = ""
        else:
            body_str = json.dumps(params, separators=(",", ":"))
        
        sign_str = timestamp + self.api_key + self.recv_window + body_str
        signature = hmac.new(self.api_secret, sign_str.encode(), hashlib.sha256).hexdigest()
        return signature

    def _request(self, method: str, endpoint: str, 
                params: Dict[str, Any] = None, auth: bool = False) -> Dict[str, Any]:
        """Faz requisição HTTP autenticada ou pública."""
        params = params or {}
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if auth:
                timestamp = str(int(time.time() * 1000))
                signature = self._generate_signature(timestamp, method, endpoint, params)
                headers.update({
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-RECV-WINDOW": self.recv_window
                })

            if method == "GET":
                resp = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                resp = requests.post(url, json=params, headers=headers, timeout=10)

            resp.raise_for_status()
            data = resp.json()

            if data.get("retCode") != 0:
                log_error(f"Bybit API error {data.get('retCode')}: {data.get('retMsg')}")
                return {"retCode": -1, "retMsg": data.get("retMsg", "Unknown error")}

            return data
        except requests.RequestException as e:
            log_error(f"Request failed", e)
            return {"retCode": -1, "retMsg": str(e)}

    def get_ticker(self, symbol: str = SYMBOL) -> Decimal:
        """Obtém últwmo preço do par."""
        endpoint = "/v5/market/tickers"
        params = {"category": CATEGORY, "symbol": symbol}
        
        data = self._request("GET", endpoint, params=params, auth=False)
        try:
            if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                price = Decimal(data["result"]["list"][0]["lastPrice"])
                return price
        except (KeyError, IndexError, ValueError) as e:
            log_error(f"Failed to parse ticker price", e)
        return Decimal("0")

    def get_balance(self, coin: str = "USDT") -> Decimal:
        """Obtém saldo de uma moeda."""
        endpoint = "/v5/account/wallet-balance"
        params = {"accountType": "UNIFIED"}
        
        data = self._request("GET", endpoint, params=params, auth=True)
        try:
            if data.get("retCode") == 0:
                for account in data["result"]["list"]:
                    for coin_info in account.get("coin", []):
                        if coin_info["coin"] == coin:
                            return Decimal(coin_info["walletBalance"])
        except (KeyError, TypeError) as e:
            log_error(f"Failed to parse balance", e)
        return Decimal("0")

    def place_market_order(self, side: str, qty: Decimal,
                          symbol: str = SYMBOL) -> Dict[str, Any]:
        """Coloca ordem market (compra ou venda)."""
        endpoint = "/v5/order/create"
        params = {
            "category": CATEGORY,
            "symbol": symbol,
            "side": side,
            "orderType": "Market",
            "qty": str(qty),
            "timeInForce": "IOC"
        }
        
        data = self._request("POST", endpoint, params=params, auth=True)
        if data.get("retCode") == 0:
            log(f"Order placed: {side} {qty} {symbol}")
            return data
        else:
            log_error(f"Failed to place order: {data.get('retMsg')}")
            return data

    def get_klines(self, symbol: str = SYMBOL, interval: str = "1", 
                   limit: int = 100) -> List[List[Any]]:
        """Obtém K-lines (candles) históricos."""
        endpoint = "/v5/market/kline"
        params = {
            "category": CATEGORY,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        data = self._request("GET", endpoint, params=params, auth=False)
        try:
            if data.get("retCode") == 0:
                return data["result"]["list"]
        except (KeyError, TypeError) as e:
            log_error(f"Failed to parse klines", e)
        return []
