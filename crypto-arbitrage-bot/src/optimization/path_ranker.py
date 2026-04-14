"""Machine learning path ranking for optimal trade selection"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from dataclasses import dataclass
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class RankedPath:
    """Ranked arbitrage path with confidence score"""
    path: str
    exchange: str
    profit_pct: float
    profit_usd: float
    confidence: float
    risk_score: float
    expected_execution_time_ms: float
    liquidity_score: float
    final_rank: float
    type: str = "Unknown"

class PathRanker:
    """Intelligent path ranking using ML models"""
    
    def __init__(self, model_path: str = "models/path_ranker.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.load_or_train_model()
        
    def load_or_train_model(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info("✅ Loaded existing path ranking model")
            except:
                logger.info("🔄 Training new path ranking model")
                self.train_model()
        else:
            logger.info("🔄 Models directory not found or model missing. Training new one.")
            self.train_model()
    
    def extract_features(self, opportunity: Dict, market_data: Dict) -> np.ndarray:
        """Extract features for ML model"""
        features = [
            opportunity.get("profit_pct", 0),
            opportunity.get("profit_usd", 0),
            market_data.get("volatility_5min", 0),
            market_data.get("spread_pct", 0),
            market_data.get("volume_24h", 0),
            market_data.get("liquidity_depth", 0),
            market_data.get("order_book_imbalance", 0),
            market_data.get("historical_success_rate", 0.95),
            1.0 / (1 + market_data.get("competition_level", 0.5)),
            market_data.get("time_of_day_factor", 1.0),
        ]
        return np.array(features).reshape(1, -1)
    
    def predict_success_probability(self, opportunity: Dict, market_data: Dict) -> float:
        """Predict probability of successful execution"""
        if self.model is None:
            return 0.85  # Default confidence
        
        try:
            features = self.extract_features(opportunity, market_data)
            scaled_features = self.scaler.transform(features)
            # RandomForestRegressor predict target 0-1
            prediction = self.model.predict(scaled_features)[0]
            return float(np.clip(prediction, 0, 1))
        except:
            return 0.85
    
    def calculate_risk_score(self, opportunity: Dict, market_data: Dict) -> float:
        """Calculate risk score (0-1, lower is better)"""
        risk_factors = [
            market_data.get("volatility_5min", 0.1) * 2,
            market_data.get("spread_pct", 0.05) * 10,
            1.0 - market_data.get("liquidity_depth", 500000) / 1000000,
            opportunity.get("profit_pct", 0.5) * 0.5,
        ]
        return float(np.clip(np.mean(risk_factors), 0, 1))
    
    def calculate_liquidity_score(self, symbol: str, market_data: Dict) -> float:
        """Calculate liquidity score based on order book depth"""
        depth = market_data.get(f"{symbol}_depth", 500000)
        volume = market_data.get(f"{symbol}_volume_24h", 1000000)
        return float(np.clip((depth + volume) / 2000000, 0, 1))
    
    def estimate_execution_time(self, opportunity: Dict, market_data: Dict) -> float:
        """Estimate execution time in milliseconds"""
        base_time = 50.0
        volatility_factor = 1 + market_data.get("volatility_5min", 0.1) * 2
        liquidity_factor = 2 - self.calculate_liquidity_score(opportunity.get("symbol", "BTC"), market_data)
        return float(np.clip(base_time * volatility_factor * liquidity_factor, 50, 500))
    
    def rank_paths(self, opportunities: List[Dict], market_data: Dict) -> List[RankedPath]:
        """Rank multiple arbitrage paths by profitability + safety"""
        ranked_paths = []
        
        for opp in opportunities:
            confidence = self.predict_success_probability(opp, market_data)
            risk_score = self.calculate_risk_score(opp, market_data)
            liquidity_score = self.calculate_liquidity_score(opp.get("symbol", "BTC"), market_data)
            exec_time = self.estimate_execution_time(opp, market_data)
            
            profit_normalized = np.clip(opp.get("profit_pct", 0) / 5.0, 0, 1)
            
            final_rank = (
                profit_normalized * 0.40 +
                confidence * 0.30 +
                liquidity_score * 0.20 +
                (1 - risk_score) * 0.10
            )
            
            ranked_paths.append(RankedPath(
                path=opp.get("path", "Unknown"),
                exchange=opp.get("exchange", "Unknown"),
                profit_pct=opp.get("profit_pct", 0.0),
                profit_usd=opp.get("profit_usd", 0.0),
                confidence=confidence,
                risk_score=risk_score,
                expected_execution_time_ms=exec_time,
                liquidity_score=liquidity_score,
                final_rank=final_rank,
                type=opp.get("type", "Unknown")
            ))
        
        ranked_paths.sort(key=lambda x: x.final_rank, reverse=True)
        return ranked_paths
    
    def train_model(self, historical_data: pd.DataFrame = None):
        """Train ML model on historical trade data"""
        if historical_data is None:
            historical_data = self._generate_synthetic_data()
        
        cols = ['profit_pct', 'profit_usd', 'volatility', 'spread', 
                'volume', 'liquidity', 'imbalance', 'success_rate',
                'competition', 'time_factor']
        
        features = historical_data[cols].values
        targets = historical_data['execution_success'].values
        
        # Simple scaling
        self.scaler.fit(features)
        features_scaled = self.scaler.transform(features)
        
        self.model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
        self.model.fit(features_scaled, targets)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"✅ Trained and saved model to {self.model_path}")
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Generate synthetic training data"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'profit_pct': np.random.uniform(0.1, 3.0, n_samples),
            'profit_usd': np.random.uniform(1, 300, n_samples),
            'volatility': np.random.uniform(0.1, 5.0, n_samples),
            'spread': np.random.uniform(0.01, 1.0, n_samples),
            'volume': np.random.uniform(100000, 10000000, n_samples),
            'liquidity': np.random.uniform(10000, 5000000, n_samples),
            'imbalance': np.random.uniform(-0.5, 0.5, n_samples),
            'success_rate': np.random.uniform(0.5, 1.0, n_samples),
            'competition': np.random.uniform(0, 1.0, n_samples),
            'time_factor': np.random.uniform(0.5, 1.5, n_samples),
        }
        
        # Target: probability of success
        prob = (data['profit_pct']/5.0)*0.1 + (data['liquidity']/5000000)*0.5 + (1-data['volatility']/10.0)*0.4
        data['execution_success'] = np.clip(prob + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        return pd.DataFrame(data)

# Global instance
path_ranker = PathRanker()
