"""
Professional Animated Model Performance Visualizations
Save as: src/visualization/animation_generator.py
Run: python src/visualization/animation_generator.py

Features:
- Interactive animated equity curves with Play/Pause controls
- Animated prediction scatter plots with confidence intervals
- Rolling metrics animations
- Real-time performance updates
- Export to HTML and GIF
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Create directories
VIZ_PATH = Path("visualizations/animations")
VIZ_PATH.mkdir(parents=True, exist_ok=True)
HTML_PATH = VIZ_PATH / 'html'
HTML_PATH.mkdir(parents=True, exist_ok=True)
GIF_PATH = VIZ_PATH / 'gifs'
GIF_PATH.mkdir(parents=True, exist_ok=True)

# Professional color palette
COLORS = {
    'primary': '#1E88E5',
    'secondary': '#DC143C',
    'success': '#2ECC71',
    'warning': '#F39C12',
    'info': '#00ACC1',
    'dark': '#2C3E50',
    'light': '#ECF0F1',
    'purple': '#9B59B6',
    'orange': '#E67E22'
}


def create_animated_equity_curve(y_true, y_pred, window_size=50, save_path=None):
    """
    Create animated equity curve with Play/Pause controls
    
    Parameters:
    - y_true: actual returns
    - y_pred: predicted returns
    - window_size: rolling window size for animation
    - save_path: path to save the HTML/PNG
    """
    print("\n📈 Creating animated equity curve...")
    
    # Calculate cumulative returns
    cumulative_true = (1 + y_true).cumprod()
    cumulative_pred = (1 + y_pred).cumprod()
    
    # Calculate drawdown
    running_max = cumulative_pred.expanding().max()
    drawdown = (cumulative_pred - running_max) / running_max * 100
    
    # Create frames for animation
    frames = []
    n_frames = len(cumulative_true) - window_size
    
    for i in range(0, n_frames, max(1, n_frames // 50)):  # Limit to ~50 frames
        end_idx = i + window_size
        
        frame_data = [
            go.Scatter(
                x=list(range(end_idx)),
                y=cumulative_true[:end_idx],
                mode='lines',
                name='Buy & Hold',
                line=dict(color=COLORS['info'], width=2),
                showlegend=False
            ),
            go.Scatter(
                x=list(range(end_idx)),
                y=cumulative_pred[:end_idx],
                mode='lines',
                name='Model Strategy',
                line=dict(color=COLORS['success'], width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.1)',
                showlegend=False
            )
        ]
        
        frames.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    # Initial frame
    fig = go.Figure(
        data=[
            go.Scatter(
                x=list(range(window_size)),
                y=cumulative_true[:window_size],
                mode='lines',
                name='Buy & Hold',
                line=dict(color=COLORS['info'], width=2)
            ),
            go.Scatter(
                x=list(range(window_size)),
                y=cumulative_pred[:window_size],
                mode='lines',
                name='Model Strategy',
                line=dict(color=COLORS['success'], width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.1)'
            )
        ]
    )
    
    fig.frames = frames
    
    fig.update_layout(
        title=dict(
            text='<b>Animated Equity Curve</b><br><sub>Progressive cumulative returns over time</sub>',
            x=0.5,
            font=dict(size=18, family='Arial Black')
        ),
        xaxis=dict(title='Time Steps', range=[0, len(cumulative_true)]),
        yaxis=dict(title='Cumulative Return', tickformat='.0%'),
        height=500,
        width=1000,
        template='plotly_white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="▶️ Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 100, "redraw": True},
                                     "fromcurrent": True, "mode": "immediate"}]),
                    dict(label="⏸️ Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate"}]),
                    dict(label="🔄 Reset",
                         method="animate",
                         args=[["frame0"], {"frame": {"duration": 0, "redraw": True},
                                           "mode": "immediate"}])
                ],
                x=0.02,
                y=0.95,
                xanchor='left',
                yanchor='top',
                bgcolor=COLORS['primary'],
                font=dict(color='white', size=12)
            )
        ],
        sliders=[dict(
            steps=[
                dict(method="animate", label=f"{i}", args=[[f"frame{i}"], 
                      {"frame": {"duration": 100, "redraw": True}, "mode": "immediate"}])
                for i in range(0, n_frames, max(1, n_frames // 10))
            ],
            transition=dict(duration=0),
            x=0.1,
            len=0.9,
            currentvalue=dict(prefix="Progress: ", font=dict(size=12))
        )]
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"✅ Saved animated equity curve to {save_path}")
    
    fig.write_html(HTML_PATH / 'equity_curve_animated.html')
    fig.write_image(VIZ_PATH / 'equity_curve_animated.png', width=1000, height=500)
    
    return fig


def create_animated_prediction_scatter(y_true, y_pred, save_path=None):
    """
    Create animated scatter plot showing predictions over time
    
    Parameters:
    - y_true: actual returns
    - y_pred: predicted returns
    - save_path: path to save the HTML/PNG
    """
    print("\n🎯 Creating animated prediction scatter plot...")
    
    # Calculate residuals
    residuals = y_true - y_pred
    
    # Create frames for animation
    frames = []
    n_frames = min(200, len(y_true))
    
    for i in range(0, n_frames, max(1, n_frames // 50)):
        end_idx = i + 1
        
        frame_data = [
            go.Scatter(
                x=y_true[:end_idx],
                y=y_pred[:end_idx],
                mode='markers',
                marker=dict(
                    size=8,
                    color=np.abs(residuals[:end_idx]),
                    colorscale='RdYlBu_r',
                    showscale=False,
                    opacity=0.7,
                    line=dict(width=0.5, color='white')
                ),
                text=[f'Actual: {a:.4f}<br>Predicted: {p:.4f}' 
                      for a, p in zip(y_true[:end_idx], y_pred[:end_idx])],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            ),
            go.Scatter(
                x=[y_true.min(), y_true.max()],
                y=[y_true.min(), y_true.max()],
                mode='lines',
                name='Perfect Prediction',
                line=dict(color='red', width=2, dash='dash'),
                showlegend=False
            )
        ]
        
        frames.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    # Initial frame
    fig = go.Figure(
        data=[
            go.Scatter(
                x=y_true[:1],
                y=y_pred[:1],
                mode='markers',
                marker=dict(size=8, color=COLORS['primary'], opacity=0.7),
                name='Predictions'
            ),
            go.Scatter(
                x=[y_true.min(), y_true.max()],
                y=[y_true.min(), y_true.max()],
                mode='lines',
                name='Perfect Prediction',
                line=dict(color='red', width=2, dash='dash')
            )
        ]
    )
    
    fig.frames = frames
    
    fig.update_layout(
        title=dict(
            text='<b>Animated Prediction Scatter Plot</b><br><sub>Progressive predictions over time</sub>',
            x=0.5,
            font=dict(size=18, family='Arial Black')
        ),
        xaxis=dict(title='Actual Returns', tickformat='.2%', range=[y_true.min() * 1.1, y_true.max() * 1.1]),
        yaxis=dict(title='Predicted Returns', tickformat='.2%', range=[y_pred.min() * 1.1, y_pred.max() * 1.1]),
        height=500,
        width=900,
        template='plotly_white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="▶️ Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 100, "redraw": True},
                                     "fromcurrent": True, "mode": "immediate"}]),
                    dict(label="⏸️ Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate"}]),
                    dict(label="🔄 Reset",
                         method="animate",
                         args=[["frame0"], {"frame": {"duration": 0, "redraw": True},
                                           "mode": "immediate"}])
                ],
                x=0.02,
                y=0.95,
                bgcolor=COLORS['primary'],
                font=dict(color='white', size=12)
            )
        ]
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"✅ Saved animated prediction scatter to {save_path}")
    
    fig.write_html(HTML_PATH / 'prediction_scatter_animated.html')
    fig.write_image(VIZ_PATH / 'prediction_scatter_animated.png', width=900, height=500)
    
    return fig


def create_animated_rolling_metrics(y_pred, window=20, save_path=None):
    """
    Create animated rolling metrics visualization
    
    Parameters:
    - y_pred: predicted returns
    - window: rolling window size
    - save_path: path to save the HTML/PNG
    """
    print("\n📊 Creating animated rolling metrics...")
    
    # Calculate rolling metrics
    returns_series = pd.Series(y_pred)
    rolling_mean = returns_series.rolling(window).mean()
    rolling_std = returns_series.rolling(window).std()
    rolling_sharpe = rolling_mean / rolling_std * np.sqrt(252)
    rolling_win_rate = returns_series.rolling(window).apply(lambda x: (x > 0).mean()) * 100
    
    # Create frames for animation
    frames = []
    n_frames = len(y_pred) - window
    
    for i in range(0, n_frames, max(1, n_frames // 50)):
        end_idx = i + window
        
        frame_data = [
            go.Scatter(
                x=list(range(end_idx)),
                y=rolling_mean[:end_idx] * 100,
                mode='lines',
                name='Rolling Mean',
                line=dict(color=COLORS['primary'], width=2),
                fill='tozeroy',
                fillcolor='rgba(30, 136, 229, 0.2)',
                showlegend=False
            ),
            go.Scatter(
                x=list(range(end_idx)),
                y=rolling_std[:end_idx] * 100,
                mode='lines',
                name='Rolling Std',
                line=dict(color=COLORS['warning'], width=2),
                showlegend=False
            )
        ]
        
        frames.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Rolling Mean Return', 'Rolling Volatility',
                       'Rolling Sharpe Ratio', 'Rolling Win Rate'),
        vertical_spacing=0.12,
        horizontal_spacing=0.12
    )
    
    # Initial traces
    fig.add_trace(
        go.Scatter(
            x=list(range(window)),
            y=rolling_mean[:window] * 100,
            mode='lines',
            name='Mean Return',
            line=dict(color=COLORS['primary'], width=2),
            fill='tozeroy',
            fillcolor='rgba(30, 136, 229, 0.2)'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(window)),
            y=rolling_std[:window] * 100,
            mode='lines',
            name='Volatility',
            line=dict(color=COLORS['warning'], width=2)
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(window)),
            y=rolling_sharpe[:window],
            mode='lines',
            name='Sharpe Ratio',
            line=dict(color=COLORS['success'], width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(window)),
            y=rolling_win_rate[:window],
            mode='lines',
            name='Win Rate',
            line=dict(color=COLORS['info'], width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 172, 193, 0.2)'
        ),
        row=2, col=2
    )
    
    fig.frames = frames
    
    fig.update_layout(
        title=dict(
            text=f'<b>Animated Rolling Metrics ({window}-day window)</b><br><sub>Progressive performance analysis</sub>',
            x=0.5,
            font=dict(size=18, family='Arial Black')
        ),
        height=700,
        width=1100,
        template='plotly_white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="▶️ Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 100, "redraw": True},
                                     "fromcurrent": True, "mode": "immediate"}]),
                    dict(label="⏸️ Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate"}])
                ],
                x=0.02,
                y=0.98,
                bgcolor=COLORS['primary'],
                font=dict(color='white', size=12)
            )
        ]
    )
    
    fig.update_xaxes(title_text='Time Steps', row=1, col=1)
    fig.update_yaxes(title_text='Return (%)', row=1, col=1)
    fig.update_xaxes(title_text='Time Steps', row=1, col=2)
    fig.update_yaxes(title_text='Volatility (%)', row=1, col=2)
    fig.update_xaxes(title_text='Time Steps', row=2, col=1)
    fig.update_yaxes(title_text='Sharpe Ratio', row=2, col=1)
    fig.update_xaxes(title_text='Time Steps', row=2, col=2)
    fig.update_yaxes(title_text='Win Rate (%)', row=2, col=2)
    
    if save_path:
        fig.write_html(save_path)
        print(f"✅ Saved animated rolling metrics to {save_path}")
    
    fig.write_html(HTML_PATH / 'rolling_metrics_animated.html')
    fig.write_image(VIZ_PATH / 'rolling_metrics_animated.png', width=1100, height=700)
    
    return fig


def create_animated_drawdown(y_pred, save_path=None):
    """
    Create animated drawdown visualization
    
    Parameters:
    - y_pred: predicted returns
    - save_path: path to save the HTML/PNG
    """
    print("\n📉 Creating animated drawdown visualization...")
    
    # Calculate cumulative returns and drawdown
    cumulative = (1 + y_pred).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    
    # Create frames for animation
    frames = []
    n_frames = len(drawdown)
    
    for i in range(0, n_frames, max(1, n_frames // 50)):
        end_idx = i + 1
        
        frame_data = [
            go.Scatter(
                x=list(range(end_idx)),
                y=drawdown[:end_idx],
                mode='lines',
                name='Drawdown',
                line=dict(color=COLORS['secondary'], width=2),
                fill='tozeroy',
                fillcolor='rgba(220, 20, 60, 0.3)',
                showlegend=False
            )
        ]
        
        frames.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[0],
                y=[0],
                mode='lines',
                name='Drawdown',
                line=dict(color=COLORS['secondary'], width=2)
            )
        ]
    )
    
    fig.frames = frames
    
    fig.update_layout(
        title=dict(
            text='<b>Animated Drawdown Analysis</b><br><sub>Progressive drawdown visualization</sub>',
            x=0.5,
            font=dict(size=18, family='Arial Black')
        ),
        xaxis=dict(title='Time Steps', range=[0, len(drawdown)]),
        yaxis=dict(title='Drawdown (%)', range=[drawdown.min() * 1.1, 5]),
        height=500,
        width=1000,
        template='plotly_white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="▶️ Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 50, "redraw": True},
                                     "fromcurrent": True, "mode": "immediate"}]),
                    dict(label="⏸️ Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate"}])
                ],
                x=0.02,
                y=0.95,
                bgcolor=COLORS['secondary'],
                font=dict(color='white', size=12)
            )
        ]
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"✅ Saved animated drawdown to {save_path}")
    
    fig.write_html(HTML_PATH / 'drawdown_animated.html')
    fig.write_image(VIZ_PATH / 'drawdown_animated.png', width=1000, height=500)
    
    return fig


def create_animated_waterfall(y_true, y_pred, save_path=None):
    """
    Create animated waterfall plot for prediction errors
    
    Parameters:
    - y_true: actual returns
    - y_pred: predicted returns
    - save_path: path to save the HTML/PNG
    """
    print("\n💧 Creating animated waterfall plot...")
    
    errors = y_true - y_pred
    sorted_idx = np.argsort(np.abs(errors))[::-1][:10]  # Top 10 errors
    
    # Create frames for animation
    frames = []
    n_frames = len(sorted_idx)
    
    for i in range(n_frames):
        current_idx = sorted_idx[:i+1]
        current_errors = errors[current_idx]
        current_labels = [f'Point {idx}' for idx in current_idx]
        
        frame_data = [
            go.Bar(
                x=current_labels,
                y=current_errors * 100,
                marker_color=[COLORS['success'] if e > 0 else COLORS['secondary'] for e in current_errors],
                text=[f'{e*100:.2f}%' for e in current_errors],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Error: %{y:.2f}%<extra></extra>',
                showlegend=False
            )
        ]
        
        frames.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    fig = go.Figure()
    fig.frames = frames
    
    fig.update_layout(
        title=dict(
            text='<b>Animated Prediction Error Waterfall</b><br><sub>Top prediction errors by magnitude</sub>',
            x=0.5,
            font=dict(size=18, family='Arial Black')
        ),
        xaxis=dict(title='Prediction Points'),
        yaxis=dict(title='Prediction Error (%)'),
        height=500,
        width=900,
        template='plotly_white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="▶️ Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 500, "redraw": True},
                                     "fromcurrent": True, "mode": "immediate"}]),
                    dict(label="🔄 Reset",
                         method="animate",
                         args=[["frame0"], {"frame": {"duration": 0, "redraw": True},
                                           "mode": "immediate"}])
                ],
                x=0.02,
                y=0.95,
                bgcolor=COLORS['purple'],
                font=dict(color='white', size=12)
            )
        ]
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"✅ Saved animated waterfall to {save_path}")
    
    fig.write_html(HTML_PATH / 'waterfall_animated.html')
    fig.write_image(VIZ_PATH / 'waterfall_animated.png', width=900, height=500)
    
    return fig


def generate_all_animations(y_true, y_pred, save_path=None):
    """
    Generate all animated visualizations
    
    Parameters:
    - y_true: actual returns
    - y_pred: predicted returns
    - save_path: output directory (optional)
    """
    print("\n" + "="*60)
    print("🎬 Generating Complete Animation Suite")
    print("="*60)
    
    # 1. Equity Curve Animation
    create_animated_equity_curve(y_true, y_pred, save_path=HTML_PATH / 'equity_curve.html')
    
    # 2. Prediction Scatter Animation
    create_animated_prediction_scatter(y_true, y_pred, save_path=HTML_PATH / 'prediction_scatter.html')
    
    # 3. Rolling Metrics Animation
    create_animated_rolling_metrics(y_pred, save_path=HTML_PATH / 'rolling_metrics.html')
    
    # 4. Drawdown Animation
    create_animated_drawdown(y_pred, save_path=HTML_PATH / 'drawdown.html')
    
    # 5. Waterfall Animation
    create_animated_waterfall(y_true, y_pred, save_path=HTML_PATH / 'waterfall.html')
    
    print("\n" + "="*60)
    print("✅ All animations generated successfully!")
    print(f"📁 Output directory: {HTML_PATH}")
    print("="*60)


if __name__ == "__main__":
    # Demo with sample data
    np.random.seed(42)
    n_samples = 200
    
    # Generate realistic returns
    y_true = np.random.normal(0.001, 0.02, n_samples)
    y_pred = y_true + np.random.normal(0, 0.008, n_samples)
    
    # Generate all animations
    generate_all_animations(y_true, y_pred)