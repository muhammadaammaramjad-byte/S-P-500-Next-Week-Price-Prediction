"""Binance exchange implementation"""
import json
from .base import BaseExchange
from typing import Dict, Optional

class BinanceExchange(BaseExchange):
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("Binance", api_key, api_secret)
    
    def get_websocket_url(self) -> str:
        return "wss://stream.binance.com:9443/ws"
    
    async def subscribe_order_book(self, symbol: str):
        """Subscribe to order book updates"""
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@bookTicker"],
            "id": 1
        }
        await self.websocket.send(json.dumps(subscribe_msg))
    
    async def execute_order(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Execute market order on Binance"""
        import requests
        endpoint = "https://api.binance.com/api/v3/order"
        
        order = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": amount
        }
        
        # response = requests.post(endpoint, params=order, 
        #                          auth=(self.api_key, self.api_secret))
        return {"status": "simulated", "order": order}
    
    def _extract_price(self, data: Dict) -> Optional[float]:
        """Extract best bid/ask from Binance bookTicker"""
        if 'b' in data and 'a' in data:
            # Best bid and ask
            return (float(data['b']) + float(data['a'])) / 2
        return None
    
    def _extract_symbol(self, data: Dict) -> str:
        return data.get('s', 'BTCUSDT')
