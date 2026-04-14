"""Real-time arbitrage opportunity detection"""
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pandas as pd
import numpy as np

class ArbitrageDetector:
    """Detect price discrepancies across exchanges"""
    
    def __init__(self, min_profit_percent: float = 0.5, min_profit_usd: float = 10):
        self.min_profit_percent = min_profit_percent
        self.min_profit_usd = min_profit_usd
        self.price_feeds: Dict[str, Dict[str, float]] = {}  # {symbol: {exchange: price}}
        self.opportunities: List[Dict] = []
        
    def update_price(self, exchange: str, symbol: str, price: float):
        """Update price feed for an exchange"""
        if symbol not in self.price_feeds:
            self.price_feeds[symbol] = {}
        self.price_feeds[symbol][exchange] = price
    
    def detect_opportunities(self) -> List[Dict]:
        """Scan for arbitrage opportunities"""
        opportunities = []
        
        for symbol, prices in self.price_feeds.items():
            if len(prices) < 2:
                continue
            
            # Find best bid (highest price) and best ask (lowest price)
            best_bid_exchange = max(prices.items(), key=lambda x: x[1])
            best_ask_exchange = min(prices.items(), key=lambda x: x[1])
            
            buy_price = best_ask_exchange[1]  # Buy from cheapest
            sell_price = best_bid_exchange[1]  # Sell to most expensive
            
            if buy_price <= 0:
                continue
                
            profit_percent = ((sell_price - buy_price) / buy_price) * 100
            profit_usd = sell_price - buy_price
            
            if profit_percent >= self.min_profit_percent and profit_usd >= self.min_profit_usd:
                opportunities.append({
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "buy_exchange": best_ask_exchange[0],
                    "sell_exchange": best_bid_exchange[0],
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "profit_percent": profit_percent,
                    "profit_usd": profit_usd,
                    "status": "pending"
                })
        
        return opportunities
    
    async def run(self, callback):
        """Continuously scan for opportunities"""
        while True:
            opportunities = self.detect_opportunities()
            for opp in opportunities:
                await callback(opp)
            await asyncio.sleep(0.1)  # Check every 100ms
