"""Test suite for atomic trade execution"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.execution.atomic_trader import AtomicTradeExecutor, TradeStatus, AtomicTrade

class TestAtomicTradeExecutor:
    
    def setup_method(self):
        """Setup mock exchange client"""
        self.mock_exchange = Mock()
        self.mock_exchange.execute_order = AsyncMock()
        self.mock_exchange.get_ticker = AsyncMock()
        
        self.executor = AtomicTradeExecutor(self.mock_exchange, retry_count=1)
        # Mocking protected method for market price
        self.executor._get_market_price = AsyncMock(return_value=45000.0)
    
    @pytest.mark.asyncio
    async def test_successful_triangle_execution(self):
        """Test complete triangular trade execution"""
        
        # Mock order responses
        self.mock_exchange.execute_order.side_effect = [
            {"id": "order1", "executed_qty": 0.1, "price": 45000},
            {"id": "order2", "executed_qty": 2.5, "price": 0.05},
            {"id": "order3", "executed_qty": 2250, "price": 2250}
        ]
        
        opportunity = {
            "exchange": "Binance",
            "path": "USDT-BTC-ETH-USDT",
            "start_amount": 1000,
            "profit_usd": 12.50,
            "profit_pct": 1.25
        }
        
        trade = await self.executor.execute_triangular_trade(opportunity)
        
        assert trade.status == TradeStatus.COMPLETED
        assert len(trade.executed_orders) == 3
        assert self.mock_exchange.execute_order.call_count == 3
    
    @pytest.mark.asyncio
    async def test_rollback_on_failure(self):
        """Test automatic rollback when trade fails mid-execution"""
        
        # Mock first order success, second order fails
        self.mock_exchange.execute_order.side_effect = [
            {"id": "order1", "executed_qty": 0.1, "price": 45000},
            Exception("Insufficient liquidity"),
            {"id": "rollback1", "executed_qty": 0.1, "price": 45050}
        ]
        
        opportunity = {
            "exchange": "Binance",
            "path": "USDT-BTC-ETH-USDT",
            "start_amount": 1000,
            "profit_usd": 12.50,
            "profit_pct": 1.25
        }
        
        trade = await self.executor.execute_triangular_trade(opportunity)
        
        assert trade.status == TradeStatus.ROLLED_BACK
        assert trade.error_message is not None
        # Should call execute_order for the first step's rollback
        assert self.mock_exchange.execute_order.call_count == 3 

    def test_parse_triangle_path(self):
        """Test path parsing into executable steps"""
        steps = self.executor._parse_steps("USDT-BTC-ETH-USDT")
        assert len(steps) == 3

    def test_performance_stats(self):
        """Test performance tracking"""
        self.executor.trade_history = [
            AtomicTrade(id="1", exchange="Binance", path="test", start_amount=1000,
                       start_currency="USDT", steps=[], status=TradeStatus.COMPLETED,
                       current_step=0, executed_orders=[], created_at=datetime.now(),
                       completed_at=datetime.now(), profit_usd=10, error_message=None)
        ]
        
        stats = self.executor.get_performance_stats()
        assert stats["total_trades"] == 1
        assert stats["successful_trades"] == 1
        assert stats["total_profit"] == 10
