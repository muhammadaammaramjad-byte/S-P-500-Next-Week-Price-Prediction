"""
Sentiment Features Module
Extracts sentiment from news and social media
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class SentimentAnalyzer:
    """Sentiment analysis for financial news"""
    
    def __init__(self):
        self.sentiment_cache = {}
        
    def get_sentiment(self, query: str = "S&P 500", days_back: int = 7) -> Tuple[float, float]:
        """
        Get sentiment score for S&P 500
        
        Returns:
        --------
        tuple: (polarity, subjectivity)
        """
        # Check cache
        cache_key = f"{query}_{days_back}"
        if cache_key in self.sentiment_cache:
            return self.sentiment_cache[cache_key]
        
        # Generate realistic mock sentiment based on market conditions
        # In production, this would call NewsAPI or other sources
        polarity = self._generate_mock_polarity()
        subjectivity = np.random.uniform(0.3, 0.7)
        
        # Cache result
        self.sentiment_cache[cache_key] = (polarity, subjectivity)
        
        return polarity, subjectivity
    
    def _generate_mock_polarity(self) -> float:
        """Generate realistic mock sentiment polarity"""
        # Sentiment tends to follow market trends with slight lag
        # This is a simplified simulation
        np.random.seed(int(datetime.now().timestamp()) % 10000)
        
        # Base polarity (slightly positive bias for stock market)
        base_polarity = np.random.normal(0.05, 0.1)
        
        # Add some variation
        polarity = np.clip(base_polarity, -0.5, 0.5)
        
        return polarity
    
    def add_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add sentiment features to DataFrame"""
        df = df.copy()
        
        # Get current sentiment
        polarity, subjectivity = self.get_sentiment()
        
        # Add sentiment columns
        df['sentiment_polarity'] = polarity
        df['sentiment_subjectivity'] = subjectivity
        
        # Add lagged features
        df['sentiment_lag1'] = df['sentiment_polarity'].shift(1)
        df['sentiment_lag3'] = df['sentiment_polarity'].shift(3)
        df['sentiment_lag5'] = df['sentiment_polarity'].shift(5)
        
        return df
    
    def get_sentiment_summary(self) -> Dict:
        """Get sentiment summary statistics"""
        polarity, subjectivity = self.get_sentiment()
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment_class': self._classify_sentiment(polarity),
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity"""
        if polarity > 0.1:
            return 'POSITIVE'
        elif polarity < -0.1:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'