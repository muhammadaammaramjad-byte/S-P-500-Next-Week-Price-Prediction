"""
News API Data Source

Collects news sentiment data from NewsAPI
"""

import requests
from datetime import datetime, timedelta
import pandas as pd

class NewsAPISource:
    """News API data source connector"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2/everything'
    
    def get_headlines(self, query: str = 'S&P 500', days_back: int = 7) -> pd.DataFrame:
        """Get news headlines"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': from_date,
            'language': 'en',
            'sortBy': 'relevancy',
            'apiKey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            df = pd.DataFrame(articles)
            return df[['title', 'description', 'publishedAt']] if not df.empty else pd.DataFrame()
        
        return pd.DataFrame()