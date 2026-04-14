"""Advanced Financial Charting System"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from src.dashboard.config import config

class ChartBuilder:
    """Enterprise-grade chart factory with professional technical analysis"""
    
    @staticmethod
    def candlestick_chart(data: pd.DataFrame, title: str = "S&P 500 Market Analysis"):
        """Professional candlestick chart with volume and technical indicators"""
        
        # Create subplots: 2 rows (Price + Volume)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            subplot_titles=(None, 'Volume'), 
            row_width=[0.2, 0.7]
        )
        
        # 1. Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'] if 'open' in data.columns else data['Open'],
                high=data['high'] if 'high' in data.columns else data['High'],
                low=data['low'] if 'low' in data.columns else data['Low'],
                close=data['close'] if 'close' in data.columns else data['Close'],
                name='Market Price',
                increasing_line_color=config.THEME['success'],
                decreasing_line_color=config.THEME['danger']
            ),
            row=1, col=1
        )
        
        # 2. Moving Average (SMA 20)
        ma20 = (data['close'] if 'close' in data.columns else data['Close']).rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index, 
                y=ma20, 
                line=dict(color=config.THEME['primary'], width=2), 
                name='SMA 20'
            ),
            row=1, col=1
        )
        
        # 3. Volume
        volume = data['volume'] if 'volume' in data.columns else data['Volume']
        colors = [config.THEME['success'] if i > 0 else config.THEME['danger'] 
                  for i in (data['close'] - data['open']).fillna(0)]
        
        fig.add_trace(
            go.Bar(
                x=data.index, 
                y=volume, 
                marker_color=colors, 
                name='Volume'
            ),
            row=2, col=1
        )
        
        # Styling
        fig.update_layout(
            title=dict(text=title, font=dict(size=24, family="Inter")),
            yaxis_title="Price (USD)",
            yaxis2_title="Volume",
            height=700,
            template="plotly_white",
            showlegend=True,
            xaxis_rangeslider_visible=False,
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode='x unified'
        )
        
        # Glassmorphism/Dark theme adjustments if needed
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
        
        return fig
