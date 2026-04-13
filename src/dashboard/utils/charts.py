"""Professional charting utilities"""
import plotly.graph_objects as go
import pandas as pd
from src.dashboard.config import config

class ChartBuilder:
    """Chart factory with professional styling"""
    
    @staticmethod
    def candlestick_chart(data: pd.DataFrame, title: str = "Price Action"):
        """Professional candlestick chart"""
        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['open'] if 'open' in data.columns else data['Open'],
                high=data['high'] if 'high' in data.columns else data['High'],
                low=data['low'] if 'low' in data.columns else data['Low'],
                close=data['close'] if 'close' in data.columns else data['Close'],
                name='Price'
            )
        ])
        
        fig.update_layout(
            title=title,
            yaxis_title="Price (USD)",
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
