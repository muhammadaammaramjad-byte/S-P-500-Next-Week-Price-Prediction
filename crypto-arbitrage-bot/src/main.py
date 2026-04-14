"""Main arbitrage bot with intelligent path ranking"""
import asyncio
import os
import numpy as np
from dotenv import load_dotenv
from src.exchanges.binance import BinanceExchange
from src.arbitrage.engine import MasterEngine
from src.execution.atomic_trader import AtomicTradeExecutor
from src.optimization.path_ranker import path_ranker

# Load environment variables
load_dotenv()

async def main():
    print("START: Crypto Arbitrage Bot v3.0 - Smart Path Ranking Enabled")
    
    # Initialize components
    api_key = os.getenv("BINANCE_API_KEY", "DEMO_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY", "DEMO_SECRET")
    
    binance = BinanceExchange(api_key=api_key, api_secret=api_secret)
    # await binance.connect()
    
    engine = MasterEngine()
    executor = AtomicTradeExecutor(binance)
    
    # Track market data for ML features
    market_data = {
        "volatility_5min": 0.5,
        "spread_pct": 0.1,
        "volume_24h": 1000000,
        "liquidity_depth": 500000,
        "order_book_imbalance": 0.1,
        "historical_success_rate": 0.95,
        "competition_level": 0.3,
        "time_of_day_factor": 1.2
    }
    
    async def on_price(exchange, symbol, price):
        await engine.process_price_update(exchange, symbol, price)
        opportunities = engine.get_all_opportunities()
        
        if opportunities:
            # Rank opportunities using ML
            ranked_paths = path_ranker.rank_paths(opportunities, market_data)
            
            # Display ranking
            print(f"\nRANKED: Ranked Opportunities ({len(ranked_paths)} detected):")
            for i, path in enumerate(ranked_paths[:3], 1):
                print(f"  {i}. {path.path} | {path.exchange} | "
                      f"Profit: {path.profit_pct:.2f}% | "
                      f"Confidence: {path.confidence*100:.1f}% | "
                      f"Risk: {path.risk_score:.2f}")
            
            # Execute only the best path if confidence > 85%
            best = ranked_paths[0]
            if best.confidence > 0.85 and best.profit_pct > 0.5:
                print(f"\nEXECUTE: EXECUTING BEST PATH: {best.path}")
                
                opportunity = {
                    "exchange": best.exchange,
                    "path": best.path,
                    "profit_pct": best.profit_pct,
                    "profit_usd": best.profit_usd,
                    "start_amount": 1000
                }
                
                # trade = await executor.execute_triangular_trade(opportunity)
                # print(f"Trade result: {trade.status.value}")
    
    binance.register_callback(on_price)
    print("Intelligent bot is active and ranking paths...")
    
    # Simulation tick
    await on_price("Binance", "BTCUSDT", 40000)
    await on_price("Binance", "ETHBTC", 0.05)
    await on_price("Binance", "ETHUSDT", 2300) # (1/40k) * (1/0.05) * 2300 = 1.15 (15% profit!)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
