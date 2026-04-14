"""Coinbase exchange implementation"""
from .base import BaseExchange
import json

class CoinbaseExchange(BaseExchange):
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("Coinbase", api_key, api_secret)
    
    def get_websocket_url(self) -> str:
        return "wss://ws-feed.pro.coinbase.com"
    
    async def subscribe_order_book(self, symbol: str):
        subscribe_msg = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": [symbol]}]
        }
        await self.websocket.send(json.dumps(subscribe_msg))
    
    async def execute_order(self, symbol: str, side: str, amount: float, price: float) -> dict:
        return {"status": "simulated", "side": side, "amount": amount}
    
    def _extract_price(self, data: dict) -> float:
        if data.get('type') == 'ticker':
            return float(data.get('price', 0))
        return None
    
    def _extract_symbol(self, data: dict) -> str:
        return data.get('product_id', 'BTC-USD').replace('-', '')
