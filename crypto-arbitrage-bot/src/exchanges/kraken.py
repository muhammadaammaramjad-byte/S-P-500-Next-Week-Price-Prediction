"""Kraken exchange implementation"""
from .base import BaseExchange
import json

class KrakenExchange(BaseExchange):
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("Kraken", api_key, api_secret)
    
    def get_websocket_url(self) -> str:
        return "wss://ws.kraken.com"
    
    async def subscribe_order_book(self, symbol: str):
        subscribe_msg = {
            "event": "subscribe",
            "pair": [symbol],
            "subscription": {"name": "ticker"}
        }
        await self.websocket.send(json.dumps(subscribe_msg))
    
    async def execute_order(self, symbol: str, side: str, amount: float, price: float) -> dict:
        return {"status": "simulated"}
    
    def _extract_price(self, data: dict) -> float:
        if isinstance(data, list) and len(data) > 1:
            # Kraken ticker format: [channel_id, {a: [price, whole_lot_volume, lot_volume], b: [...]}, ...]
            ticker_data = data[1]
            if 'a' in ticker_data and 'b' in ticker_data:
                return (float(ticker_data['a'][0]) + float(ticker_data['b'][0])) / 2
        return None
    
    def _extract_symbol(self, data: dict) -> str:
        if isinstance(data, list) and len(data) > 3:
            return data[3].replace('/', '')
        return "BTCUSDT"
