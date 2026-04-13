"""
Fundamental Indicators Module
Extracts fundamental data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional


class FundamentalIndicators:
    """Fundamental indicator extractor"""
    
    def __init__(self, ticker: str = "^GSPC"):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        
    def get_pe_ratio(self) -> Optional[float]:
        """Get P/E ratio"""
        try:
            info = self.stock.info
            return info.get('trailingPE')
        except:
            return None
    
    def get_earnings_yield(self) -> Optional[float]:
        """Get earnings yield (1/PE)"""
        pe = self.get_pe_ratio()
        if pe and pe > 0:
            return 1 / pe
        return None
    
    def get_dividend_yield(self) -> Optional[float]:
        """Get dividend yield"""
        try:
            info = self.stock.info
            return info.get('dividendYield')
        except:
            return None
    
    def get_price_to_book(self) -> Optional[float]:
        """Get price-to-book ratio"""
        try:
            info = self.stock.info
            return info.get('priceToBook')
        except:
            return None
    
    def get_price_to_sales(self) -> Optional[float]:
        """Get price-to-sales ratio"""
        try:
            info = self.stock.info
            return info.get('priceToSalesTrailing12Months')
        except:
            return None
    
    def get_all_fundamentals(self) -> Dict[str, float]:
        """Get all fundamental indicators"""
        fundamentals = {
            'PE_ratio': self.get_pe_ratio(),
            'earnings_yield': self.get_earnings_yield(),
            'dividend_yield': self.get_dividend_yield(),
            'price_to_book': self.get_price_to_book(),
            'price_to_sales': self.get_price_to_sales()
        }
        
        # Remove None values
        return {k: v for k, v in fundamentals.items() if v is not None}