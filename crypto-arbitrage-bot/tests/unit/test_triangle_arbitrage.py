"""Comprehensive test suite for triangular arbitrage detection"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.arbitrage.triangle import TriangleDetector
from src.arbitrage.engine import MasterEngine

class TestTriangleDetector:
    """Test triangular arbitrage detection logic"""
    
    def setup_method(self):
        """Initialize detector before each test"""
        self.detector = TriangleDetector("Binance", min_profit=0.5)
    
    def test_profitable_triangle_detection(self):
        """Test detection of profitable BTC-ETH-USDT triangle"""
        # USDT -> BTC -> ETH -> USDT
        self.detector.update_price("BTCUSDT", 40000)   # Cheap BTC
        self.detector.update_price("ETHBTC", 0.06)    # Cheap ETH relative to BTC
        self.detector.update_price("ETHUSDT", 2500)   # Expensive ETH in USDT
        
        opportunities = self.detector.find_opportunities()
        
        assert len(opportunities) >= 1
        assert opportunities[0]["profit_pct"] > 0.5
        assert opportunities[0]["type"] == "triangular"
        assert opportunities[0]["exchange"] == "Binance"
    
    def test_unprofitable_triangle(self):
        """Test that unprofitable triangles are NOT detected"""
        # Fair market prices (no arbitrage)
        self.detector.update_price("BTCUSDT", 45000)
        self.detector.update_price("ETHBTC", 0.05)
        self.detector.update_price("ETHUSDT", 2250)
        
        opportunities = self.detector.find_opportunities()
        assert len(opportunities) == 0
    
    def test_missing_price_data(self):
        """Test handling of incomplete price data"""
        self.detector.update_price("BTCUSDT", 45000)
        self.detector.update_price("ETHUSDT", 2250)
        
        opportunities = self.detector.find_opportunities()
        assert len(opportunities) == 0
    
    def test_zero_price_handling(self):
        """Test protection against division by zero"""
        self.detector.update_price("BTCUSDT", 0)
        self.detector.update_price("ETHBTC", 0.05)
        self.detector.update_price("ETHUSDT", 2250)
        
        opportunities = self.detector.find_opportunities()
        assert len(opportunities) == 0
    
    def test_high_profit_scenario(self):
        """Test extreme profit scenario (> 5%)"""
        self.detector.update_price("BTCUSDT", 35000)
        self.detector.update_price("ETHBTC", 0.055)
        self.detector.update_price("ETHUSDT", 2600)
        
        opportunities = self.detector.find_opportunities()
        assert len(opportunities) >= 1
        assert opportunities[0]["profit_pct"] > 5.0
    
    def test_multiple_paths(self):
        """Test detection of different triangular paths"""
        self.detector.update_price("BTCUSDT", 40000)
        self.detector.update_price("ETHBTC", 0.0625)
        self.detector.update_price("ETHUSDT", 2600)
        
        opportunities = self.detector.find_opportunities()
        assert len(opportunities) >= 1

class TestMasterEngine:
    """Test integration of cross and triangle arbitrage"""
    
    def setup_method(self):
        self.engine = MasterEngine()
    
    def test_engine_processes_both_detectors(self):
        """Test that engine updates both detector types"""
        # Note: process_price_update is async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.engine.process_price_update("Binance", "BTCUSDT", 40000))
        loop.run_until_complete(self.engine.process_price_update("Binance", "ETHBTC", 0.0625))
        loop.run_until_complete(self.engine.process_price_update("Binance", "ETHUSDT", 2600))
        
        opportunities = self.engine.get_ranked_opportunities()
        triangle_opps = [o for o in opportunities if o.type == "triangular"]
        assert len(triangle_opps) >= 1
        loop.close()

    def test_cross_exchange_arbitrage_continues(self):
        """Test cross-exchange detection still works"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.engine.process_price_update("Binance", "BTCUSDT", 45000))
        loop.run_until_complete(self.engine.process_price_update("Coinbase", "BTCUSDT", 45250))
        
        opportunities = self.engine.get_ranked_opportunities()
        cross_opps = [o for o in opportunities if o.type != "triangular"]
        assert len(cross_opps) >= 1
        loop.close()

class TestRealTimePerformance:
    """Performance benchmarks for triangle detection"""
    
    def test_detection_speed(self):
        """Test that triangle detection completes within 5ms"""
        import time
        detector = TriangleDetector("Binance")
        detector.update_price("BTCUSDT", 45000)
        detector.update_price("ETHBTC", 0.05)
        detector.update_price("ETHUSDT", 2250)
        
        start_time = time.perf_counter()
        opportunities = detector.find_opportunities()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        assert elapsed_ms < 5.0
        print(f"Triangle detection took {elapsed_ms:.2f}ms")
    
    def test_high_frequency_updates(self):
        """Test detector handles 1000 updates/second"""
        import time
        detector = TriangleDetector("Binance")
        start_time = time.perf_counter()
        
        for i in range(1000):
            detector.update_price("BTCUSDT", 45000 + i)
            detector.update_price("ETHBTC", 0.05 + (i * 0.00001))
            detector.update_price("ETHUSDT", 2250 + (i * 0.1))
            if i % 10 == 0:
                detector.find_opportunities()
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        avg_latency = elapsed_ms / 1000
        assert avg_latency < 1.0
        print(f"1000 updates averaged {avg_latency:.2f}ms each")

class TestEdgeCases:
    """Test extreme market conditions"""
    
    def test_flash_crash_scenario(self):
        """Test detector during simulated flash crash"""
        detector = TriangleDetector("Binance", min_profit=1.0)
        detector.update_price("BTCUSDT", 36000)
        detector.update_price("ETHBTC", 0.0625)
        detector.update_price("ETHUSDT", 2500)
        
        opportunities = detector.find_opportunities()
        assert len(opportunities) >= 1
        assert opportunities[0]["profit_pct"] > 5.0
    
    def test_liquidity_crisis(self):
        """Test when some pairs have zero volume"""
        detector = TriangleDetector("Binance")
        detector.update_price("BTCUSDT", 45000)
        detector.update_price("ETHBTC", 0)
        detector.update_price("ETHUSDT", 2250)
        
        opportunities = detector.find_opportunities()
        assert len(opportunities) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
