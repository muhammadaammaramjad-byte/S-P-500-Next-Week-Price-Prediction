"""Base exchange client with WebSocket support"""
import asyncio
import websockets
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseExchange(ABC):
    """Abstract base class for crypto exchanges"""
    
    def __init__(self, name: str, api_key: str = None, api_secret: str = None):
        self.name = name
        self.api_key = api_key
        self.api_secret = api_secret
        self.order_book: Dict[str, Dict] = {}
        self.price_feeds: Dict[str, float] = {}
        self.websocket = None
        self.callbacks: List[Callable] = []
        
    @abstractmethod
    def get_websocket_url(self) -> str:
        """Return WebSocket endpoint URL"""
        pass
    
    @abstractmethod
    async def subscribe_order_book(self, symbol: str):
        """Subscribe to real-time order book updates"""
        pass
    
    @abstractmethod
    async def execute_order(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Execute a trade on the exchange"""
        pass
    
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.websocket = await websockets.connect(self.get_websocket_url())
            logger.info(f"✅ Connected to {self.name} WebSocket")
            asyncio.create_task(self._listen())
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.name}: {e}")
    
    async def _listen(self):
        """Listen for incoming WebSocket messages"""
        while self.websocket:
            try:
                message = await self.websocket.recv()
                await self._process_message(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"⚠️ WebSocket disconnected for {self.name}, reconnecting...")
                await self.connect()
            except Exception as e:
                logger.error(f"Error processing message from {self.name}: {e}")
    
    async def _process_message(self, raw_message: str):
        """Process incoming WebSocket data"""
        try:
            data = json.loads(raw_message)
            
            # Extract price data (exchange-specific implementation)
            price = self._extract_price(data)
            if price:
                symbol = self._extract_symbol(data)
                self.price_feeds[symbol] = price
                
                # Notify callbacks
                for callback in self.callbacks:
                    await callback(self.name, symbol, price)
        except Exception as e:
            pass
    
    def register_callback(self, callback: Callable):
        """Register price update callback"""
        self.callbacks.append(callback)
    
    @abstractmethod
    def _extract_price(self, data: Dict) -> Optional[float]:
        """Extract price from exchange-specific message format"""
        pass
    
    @abstractmethod
    def _extract_symbol(self, data: Dict) -> str:
        """Extract symbol from exchange-specific message format"""
        pass
