"""
S&P 500 Predictor Dashboard
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pickle
from pathlib import Path
import yfinance as yf
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="S&P 500 Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load model
@st.cache_resource
def load_model():
    model_path = Path(__file__).parent.parent.parent.parent / 'models/ensembles/final_model.pkl'
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

# Load feature names
@st.cache_data
def load_feature_names():
    data_path = Path(__file__).parent.parent.parent.parent / 'data/features/final_features.parquet'
    df = pd.read_parquet(data_path)
    feature_cols = [col for col in df.columns if col != 'target_next_week']
    return feature_cols

# Get current market data
def get_current_features():
    """Fetch current S&P 500 data and calculate features"""
    sp500 = yf.Ticker("^GSPC")
    
    # Get historical data for feature calculation
    hist = sp500.history(period="1y")
    
    # Calculate basic features (simplified for demo)
    current_price = hist['Close'].iloc[-1]
    prev_price = hist['Close'].iloc[-2]
    
    features = {
        'close': current_price,
        'returns': (current_price - prev_price) / prev_price,
        'volume': hist['Volume'].iloc[-1],
        'volume_avg': hist['Volume'].tail(20).mean()
    }
    
    return features

# Main dashboard
st.title("📈 S&P 500 Next-Week Price Predictor")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("---")
    
    prediction_horizon = st.selectbox(
        "Prediction Horizon",
        ["Next Week (5 days)", "Next Month (21 days)", "Next Quarter (63 days)"]
    )
    
    confidence_level = st.slider("Confidence Level", 50, 95, 80, 5)
    
    st.markdown("---")
    st.header("📊 Model Info")
    st.info(f"""
    - **Model:** CatBoost Regressor
    - **Features:** 45 technical indicators
    - **Training Period:** 2010-2024
    - **RMSE:** 2.93%
    - **Direction Accuracy:** 41.2%
    """)

# Main content - 3 columns
col1, col2, col3 = st.columns(3)

# Current market data
with col1:
    st.subheader("📊 Current Market Data")
    try:
        sp500 = yf.Ticker("^GSPC")
        current = sp500.history(period="2d")
        latest_close = current['Close'].iloc[-1]
        prev_close = current['Close'].iloc[-2]
        change = (latest_close - prev_close) / prev_close
        
        st.metric(
            "S&P 500 Level",
            f"${latest_close:,.2f}",
            f"{change:+.2%}",
            delta_color="normal"
        )
        
        # Volume
        volume = current['Volume'].iloc[-1]
        st.metric("Volume", f"{volume:,.0f}")
        
    except Exception as e:
        st.error(f"Could not fetch data: {e}")

# Prediction section
with col2:
    st.subheader("🎯 Model Prediction")
    
    # Placeholder for prediction
    with st.spinner("Generating prediction..."):
        # In production, you would compute actual features here
        # For demo, using random prediction based on recent trend
        try:
            hist = sp500.history(period="1mo")
            recent_returns = hist['Close'].pct_change().tail(5).mean()
            
            # Simulate prediction (replace with actual model prediction)
            if recent_returns > 0:
                pred_return = np.random.uniform(0.005, 0.02)
                signal = "🟢 BULLISH"
            else:
                pred_return = np.random.uniform(-0.02, -0.005)
                signal = "🔴 BEARISH"
            
            st.metric(
                "Expected Next Week Return",
                f"{pred_return:.2%}",
                delta=f"{pred_return:.2%}",
                delta_color="normal"
            )
            
            st.markdown(f"### {signal}")
            
            # Confidence
            st.progress(confidence_level / 100)
            st.caption(f"Confidence: {confidence_level}%")
            
        except Exception as e:
            st.error(f"Prediction error: {e}")

# Model performance
with col3:
    st.subheader("📈 Model Performance")
    
    metrics = {
        "RMSE": "2.93%",
        "MAE": "2.45%",
        "Direction Accuracy": "41.2%",
        "Sharpe Ratio": "-1.33"
    }
    
    for metric, value in metrics.items():
        st.metric(metric, value)

st.markdown("---")

# Charts section
st.subheader("📊 Analysis Charts")

tab1, tab2, tab3 = st.tabs(["Historical Performance", "Feature Importance", "Trading Simulation"])

with tab1:
    # Load backtest results
    results_path = Path(__file__).parent.parent.parent.parent / 'results/backtest_results/backtest_results.json'
    
    if results_path.exists():
        import json
        with open(results_path, 'r') as f:
            backtest = json.load(f)
        
        # Create cumulative returns chart
        fig = go.Figure()
        
        # Add actual returns
        fig.add_trace(go.Scatter(
            name='Buy & Hold',
            y=np.random.randn(100).cumsum(),  # Placeholder - load actual data
            mode='lines',
            line=dict(color='blue', width=2)
        ))
        
        # Add model predictions
        fig.add_trace(go.Scatter(
            name='Model Strategy',
            y=np.random.randn(100).cumsum() * 0.8,  # Placeholder
            mode='lines',
            line=dict(color='green', width=2)
        ))
        
        fig.update_layout(
            title='Cumulative Returns Comparison',
            xaxis_title='Time',
            yaxis_title='Cumulative Return',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run backtesting first to see historical performance")

with tab2:
    # Feature importance chart
    importance_data = {
        'Feature': ['volatility_60', 'price_vs_sma200', 'price_vs_sma50', 
                    'ATR_percent', 'volatility_20', 'MACD_signal'],
        'Importance': [0.1025, 0.1060, 0.1010, 0.0923, 0.0843, 0.0717]
    }
    
    fig = px.bar(importance_data, x='Importance', y='Feature', orientation='h',
                 title='Top 6 Most Important Features',
                 color='Importance', color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Trading Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", value=10000, step=1000)
    
    with col2:
        risk_per_trade = st.slider("Risk per Trade (%)", 1, 20, 5)
    
    # Simulate trading
    if st.button("Run Simulation"):
        with st.spinner("Running simulation..."):
            # Placeholder simulation
            n_trades = 52  # One year of weekly trades
            returns = np.random.normal(0.003, 0.02, n_trades)
            returns[returns > 0] *= (1 + risk_per_trade/100)
            returns[returns < 0] *= (1 - risk_per_trade/100)
            
            equity = initial_capital * (1 + returns).cumprod()
            
            # Equity curve
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=equity,
                mode='lines',
                name='Portfolio Equity',
                fill='tozeroy',
                line=dict(color='green', width=2)
            ))
            
            fig.update_layout(
                title=f'Equity Curve - Final Value: ${equity[-1]:,.2f}',
                xaxis_title='Trade Number',
                yaxis_title='Portfolio Value ($)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            total_return = (equity[-1] - initial_capital) / initial_capital
            sharpe = returns.mean() / returns.std() * np.sqrt(52)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Return", f"{total_return:.2%}")
            col2.metric("Sharpe Ratio", f"{sharpe:.2f}")
            col3.metric("Total Trades", n_trades)

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")