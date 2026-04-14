"""Master Arbitrage Engine"""
from .detector import ArbitrageDetector
from .triangle import TriangleDetector
from ..optimization.path_ranker import PathRanker, RankedPath
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MasterEngine:
    """Enterprise Master Engine for Intelligent Arbitrage"""
    
    def __init__(self):
        self.cross_detector = ArbitrageDetector()
        self.triangle_detectors: Dict[str, TriangleDetector] = {
            "Binance": TriangleDetector("Binance"),
            "Coinbase": TriangleDetector("Coinbase")
        }
        self.ranker = PathRanker()
        
    async def process_price_update(self, exchange: str, symbol: str, price: float):
        """Process live price updates from websocket feeds"""
        # 1. Update Cross-Exchange Detector
        self.cross_detector.update_price(exchange, symbol, price)
        
        # 2. Update Triangle Detector for specific exchange
        if exchange in self.triangle_detectors:
            self.triangle_detectors[exchange].update_price(symbol, price)
            
    def get_ranked_opportunities(self) -> List[RankedPath]:
        """Detect and rank all current opportunities using ML"""
        all_opps = self.cross_detector.detect_opportunities()
        for td in self.triangle_detectors.values():
            all_opps.extend(td.find_opportunities())
            
        if not all_opps:
            return []
            
        # Mock market data for ranking context
        # In production, this would come from a dedicated market data aggregator
        market_data = {
            "volatility_5min": 0.12,
            "spread_pct": 0.05,
            "volume_24h": 1000000,
            "liquidity_depth": 750000,
            "competition_level": 0.4
        }
        
        return self.ranker.rank_paths(all_opps, market_data)
