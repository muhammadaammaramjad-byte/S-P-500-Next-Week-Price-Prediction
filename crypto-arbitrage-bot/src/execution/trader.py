"""Automated trade execution with risk controls"""
import asyncio
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TradeExecutor:
    """Execute arbitrage trades with risk management"""
    
    def __init__(self, max_position_usd: float = 1000, max_daily_trades: int = 50):
        self.max_position_usd = max_position_usd
        self.max_daily_trades = max_daily_trades
        self.daily_trades = 0
        self.daily_profit = 0.0
        self.active_positions = {}
        
    async def execute_arbitrage(self, opportunity: Dict, exchanges: Dict):
        """Execute the arbitrage trade"""
        
        # Risk checks
        if self.daily_trades >= self.max_daily_trades:
            logger.warning("Daily trade limit reached")
            return False
        
        if opportunity['buy_price'] <= 0:
            return False
            
        position_size = min(
            self.max_position_usd / opportunity['buy_price'],
            0.01  # Max position size per trade
        )
        
        try:
            # Buy on cheap exchange
            buy_exchange = exchanges[opportunity['buy_exchange']]
            buy_order = await buy_exchange.execute_order(
                symbol=opportunity['symbol'],
                side='buy',
                amount=position_size,
                price=opportunity['buy_price']
            )
            
            # Sell on expensive exchange
            sell_exchange = exchanges[opportunity['sell_exchange']]
            sell_order = await sell_exchange.execute_order(
                symbol=opportunity['symbol'],
                side='sell',
                amount=position_size,
                price=opportunity['sell_price']
            )
            
            # Record trade
            profit = (opportunity['sell_price'] - opportunity['buy_price']) * position_size
            self.daily_trades += 1
            self.daily_profit += profit
            
            logger.info(f"✅ ARBITRAGE EXECUTED: {opportunity['symbol']} | "
                       f"Profit: ${profit:.2f} | Total Daily: ${self.daily_profit:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trade failed: {e}")
            return False
    
    def get_daily_stats(self) -> Dict:
        """Get daily trading statistics"""
        return {
            "trades": self.daily_trades,
            "profit": self.daily_profit,
            "remaining_trades": self.max_daily_trades - self.daily_trades
        }
