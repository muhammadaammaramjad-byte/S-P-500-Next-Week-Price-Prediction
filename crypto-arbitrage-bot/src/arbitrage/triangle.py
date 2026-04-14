"""Intra-exchange triangular arbitrage detection with multiple paths"""
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from itertools import permutations

logger = logging.getLogger(__name__)

class TriangleDetector:
    """Detects arbitrage loops across multiple trading pairs"""
    
    # Define possible triangular paths
    PATHS = [
        {
            "name": "USDT-BTC-ETH-USDT",
            "steps": [
                ("USDT", "BTC", "BTCUSDT"),      # Buy BTC with USDT
                ("BTC", "ETH", "ETHBTC"),        # Buy ETH with BTC
                ("ETH", "USDT", "ETHUSDT")       # Sell ETH for USDT
            ]
        },
        {
            "name": "USDT-ETH-BTC-USDT",
            "steps": [
                ("USDT", "ETH", "ETHUSDT"),      # Buy ETH with USDT
                ("ETH", "BTC", "ETHBTC"),        # Buy BTC with ETH (inverse)
                ("BTC", "USDT", "BTCUSDT")       # Sell BTC for USDT
            ]
        }
    ]
    
    def __init__(self, exchange_name: str, min_profit: float = 0.5, fee_rate: float = 0.001):
        self.exchange_name = exchange_name
        self.min_profit = min_profit  # Minimum profit percentage (e.g., 0.5%)
        self.fee_rate = fee_rate      # Trading fee (e.g., 0.1% = 0.001)
        self.prices: Dict[str, float] = {}
        self.last_update = datetime.now()
        
    def update_price(self, symbol: str, price: float):
        """Update price for a specific pair"""
        if price > 0:  # Only update valid prices
            self.prices[symbol] = price
            self.last_update = datetime.now()
    
    def calculate_path_profit(self, path: Dict, start_amount: float = 1000.0) -> Optional[Dict]:
        """Calculate profit for a given triangular path"""
        try:
            current_amount = start_amount
            
            for from_currency, to_currency, pair in path["steps"]:
                if pair not in self.prices:
                    return None
                
                price = self.prices[pair]
                
                # Determine if we're buying or selling
                if pair.startswith(from_currency):
                    # Buying: from_currency -> to_currency
                    current_amount = current_amount / price
                else:
                    # Selling: to_currency -> from_currency (use inverse)
                    current_amount = current_amount * price
                
                # Apply trading fee
                current_amount *= (1 - self.fee_rate)
            
            profit = current_amount - start_amount
            profit_pct = (profit / start_amount) * 100
            
            if profit_pct >= self.min_profit:
                return {
                    "exchange": self.exchange_name,
                    "type": "triangular",
                    "path": path["name"],
                    "profit_pct": profit_pct,
                    "profit_usd": profit,
                    "start_amount": start_amount,
                    "end_amount": current_amount,
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except (KeyError, ZeroDivisionError) as e:
            logger.debug(f"Path calculation error: {e}")
            return None
    
    def find_opportunities(self) -> List[Dict]:
        """Scan all possible triangular paths for arbitrage"""
        opportunities = []
        
        for path in self.PATHS:
            result = self.calculate_path_profit(path)
            if result:
                opportunities.append(result)
        
        return opportunities
    
    def get_best_opportunity(self) -> Optional[Dict]:
        """Return the most profitable opportunity"""
        opportunities = self.find_opportunities()
        if not opportunities:
            return None
        return max(opportunities, key=lambda x: x["profit_pct"])
