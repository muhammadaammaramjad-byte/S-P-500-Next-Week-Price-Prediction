"""Atomic triangular trade execution with rollback capability"""
import asyncio
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    PENDING = "pending"
    STEP1_COMPLETE = "step1_complete"
    STEP2_COMPLETE = "step2_complete"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class AtomicTrade:
    """Represents a single atomic arbitrage trade"""
    id: str
    exchange: str
    path: str
    start_amount: float
    start_currency: str
    steps: List[Dict]
    status: TradeStatus
    current_step: int
    executed_orders: List[Dict]
    created_at: datetime
    completed_at: Optional[datetime]
    profit_usd: float
    error_message: Optional[str]

class AtomicTradeExecutor:
    """Executes multi-step trades with atomic guarantees"""
    
    def __init__(self, exchange_client, max_slippage: float = 0.005, retry_count: int = 3):
        self.exchange = exchange_client
        self.max_slippage = max_slippage  # 0.5% max slippage
        self.retry_count = retry_count
        self.active_trades: Dict[str, AtomicTrade] = {}
        self.trade_history: List[AtomicTrade] = []
        
    async def execute_triangular_trade(self, opportunity: Dict) -> AtomicTrade:
        """Execute a triangular arbitrage trade atomically"""
        
        # Create trade record
        trade_id = self._generate_trade_id(opportunity)
        trade = AtomicTrade(
            id=trade_id,
            exchange=opportunity["exchange"],
            path=opportunity["path"],
            start_amount=opportunity["start_amount"],
            start_currency=opportunity["path"].split("-")[0],
            steps=self._parse_steps(opportunity["path"]),
            status=TradeStatus.PENDING,
            current_step=0,
            executed_orders=[],
            created_at=datetime.now(),
            completed_at=None,
            profit_usd=opportunity["profit_usd"],
            error_message=None
        )
        
        self.active_trades[trade_id] = trade
        
        try:
            # Execute each step sequentially
            for step_idx, step in enumerate(trade.steps):
                trade.current_step = step_idx
                self.active_trades[trade_id] = trade
                
                order = await self._execute_step(step, trade, step_idx)
                trade.executed_orders.append(order)
                
                # Update trade status
                if step_idx == 0:
                    trade.status = TradeStatus.STEP1_COMPLETE
                elif step_idx == 1:
                    trade.status = TradeStatus.STEP2_COMPLETE
                
                # Check for slippage (if we have an expected price)
                if step.get("expected_price"):
                    actual_price = order.get("price", 0)
                    expected_price = step.get("expected_price", 0)
                    slippage = abs(actual_price - expected_price) / expected_price
                    
                    if slippage > self.max_slippage:
                        raise Exception(f"Excessive slippage: {slippage*100:.2f}% > {self.max_slippage*100:.2f}%")
            
            # All steps completed
            trade.status = TradeStatus.COMPLETED
            trade.completed_at = datetime.now()
            
            logger.info(f"✅ ATOMIC TRADE COMPLETE: {trade_id} | Profit: ${trade.profit_usd:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Trade {trade_id} failed: {e}")
            trade.status = TradeStatus.FAILED
            trade.error_message = str(e)
            
            # Attempt rollback
            await self._rollback_trade(trade)
        
        # Move to history
        self.trade_history.append(trade)
        if trade_id in self.active_trades:
            del self.active_trades[trade_id]
        
        return trade
    
    async def _execute_step(self, step: Dict, trade: AtomicTrade, step_idx: int) -> Dict:
        """Execute a single step of the triangular trade"""
        
        for attempt in range(self.retry_count):
            try:
                # Get current market price
                market_price = await self._get_market_price(step["symbol"])
                
                # Calculate amount (simplified)
                amount = trade.start_amount / market_price if step_idx == 0 else trade.executed_orders[step_idx-1]["amount"]
                
                # Execute order
                order = await self.exchange.execute_order(
                    symbol=step["symbol"],
                    side=step["side"],
                    amount=amount,
                    price=market_price
                )
                
                # Wait for fill simulation
                return {
                    "step": step_idx,
                    "symbol": step["symbol"],
                    "side": step["side"],
                    "amount": amount,
                    "price": market_price,
                    "order_id": order.get("id", "sim_id"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.warning(f"Step {step_idx} attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(0.1 * (attempt + 1))
        
        raise Exception(f"Failed to execute step {step_idx} after {self.retry_count} attempts")
    
    async def _rollback_trade(self, trade: AtomicTrade):
        """Rollback partially completed trade"""
        logger.info(f"🔄 Rolling back trade {trade.id}")
        
        try:
            # Reverse executed orders in reverse order
            for order in reversed(trade.executed_orders):
                reverse_side = "sell" if order["side"] == "buy" else "buy"
                
                await self.exchange.execute_order(
                    symbol=order["symbol"],
                    side=reverse_side,
                    amount=order["amount"],
                    price=order["price"]
                )
                
                logger.info(f"Rolled back {order['symbol']}: {reverse_side} {order['amount']}")
            
            trade.status = TradeStatus.ROLLED_BACK
            logger.info(f"✅ Trade {trade.id} successfully rolled back")
            
        except Exception as e:
            logger.error(f"💥 CRITICAL: Failed to rollback trade {trade.id}: {e}")
    
    def _parse_steps(self, path: str) -> List[Dict]:
        """Parse triangular path into executable steps"""
        currencies = path.split("-")
        steps = []
        
        # Example: USDT-BTC-ETH-USDT
        # Step 1: USDT -> BTC (Buy BTCUSDT)
        # Step 2: BTC -> ETH (Buy ETHBTC) -- wait, depends on how pairs are listed
        # This is a simplification
        for i in range(len(currencies) - 1):
            from_curr = currencies[i]
            to_curr = currencies[i + 1]
            pair = f"{to_curr}{from_curr}" if i == 0 else f"{to_curr}{from_curr}" # dummy logic
            
            steps.append({
                "from": from_curr,
                "to": to_curr,
                "symbol": f"{to_curr}{from_curr}", # Mock symbol
                "side": "buy" if i < 2 else "sell",
                "amount": 0,
                "expected_price": 0
            })
        
        return steps
    
    def _generate_trade_id(self, opportunity: Dict) -> str:
        """Generate unique trade ID"""
        data = f"{opportunity['exchange']}_{opportunity['path']}_{datetime.now().timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    async def _get_market_price(self, symbol: str) -> float:
        """Mock market price fetch"""
        return 45000.0 # Placeholder
    
    def get_performance_stats(self) -> Dict:
        """Get trade execution statistics"""
        completed = [t for t in self.trade_history if t.status == TradeStatus.COMPLETED]
        total = len(self.trade_history)
        return {
            "total_trades": total,
            "successful_trades": len(completed),
            "success_rate": len(completed) / total if total > 0 else 0,
            "total_profit": sum(t.profit_usd for t in completed)
        }
