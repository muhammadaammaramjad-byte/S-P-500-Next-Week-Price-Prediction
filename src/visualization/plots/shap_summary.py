"""
SHAP Analysis and Visualization Module
Save as: scripts/shap_analysis_animated.py
Run: python scripts/shap_analysis_animated.py

Features:
- Interactive SHAP summary plots
- Animated feature importance ranking
- 3D SHAP interaction visualization
- Waterfall plots for individual predictions
- Dependence plots with color gradients
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import shap
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Create directories
SHAP_PATH = Path("visualizations/shap")
SHAP_PATH.mkdir(parents=True, exist_ok=True)
HTML_PATH = SHAP_PATH / 'html'
HTML_PATH.mkdir(parents=True, exist_ok=True)

# Professional color palette
COLORS = {
    'shap_positive': '#E74C3C',
    'shap_negative': '#3498DB',
    'neutral': '#95A5A6',
    'primary': '#1E88E5',
    'secondary': '#DC143C',
    'warning': '#F39C12',
    'info': '#00ACC1',
    'success': '#2ECC71',
    'dark': '#2C3E50',
    'light': '#ECF0F1'
}


class AnimatedSHAPAnalyzer:
    """
    Professional Animated SHAP Analyzer for model interpretability
    
    Attributes:
        model: Trained ML model
        feature_names: List of feature names
        explainer: SHAP explainer object
        shap_values: Calculated SHAP values
        expected_value: Base expected value
    """
    
    def __init__(self, model, feature_names: List[str]):
        """
        Initialize SHAP Analyzer
        
        Args:
            model: Trained ML model (CatBoost, XGBoost, etc.)
            feature_names: List of feature names for interpretation
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
        self.expected_value = None
        
    def create_explainer(self, X_sample: np.ndarray, model_type: str = 'tree'):
        """
        Create SHAP explainer based on model type
        
        Args:
            X_sample: Sample data for explainer initialization
            model_type: Type of model ('tree', 'linear', 'deep')
        """
        print(f"🔍 Creating SHAP explainer for {model_type} model...")
        
        if model_type == 'tree':
            self.explainer = shap.TreeExplainer(self.model)
            self.shap_values = self.explainer.shap_values(X_sample)
            self.expected_value = self.explainer.expected_value
            print("✅ Using TreeExplainer")
            
        elif model_type == 'linear':
            self.explainer = shap.LinearExplainer(self.model, X_sample)
            self.shap_values = self.explainer.shap_values(X_sample)
            self.expected_value = self.explainer.expected_value
            print("✅ Using LinearExplainer")
            
        else:
            background = shap.kmeans(X_sample, 50)
            self.explainer = shap.KernelExplainer(self.model.predict, background)
            self.shap_values = self.explainer.shap_values(X_sample)
            self.expected_value = self.explainer.expected_value
            print("✅ Using KernelExplainer")
            
        return self
    
    def create_animated_summary_plot(self, X_sample: np.ndarray, 
                                      save_path: Optional[Path] = None) -> go.Figure:
        """
        Create interactive SHAP summary plot (beeswarm style)
        
        Args:
            X_sample: Sample data for plotting
            save_path: Path to save the plot (optional)
        
        Returns:
            Plotly figure object
        """
        print("\n📊 Creating animated SHAP summary plot...")
        
        # Calculate mean absolute SHAP values for sorting
        mean_shap = np.abs(self.shap_values).mean(axis=0)
        sorted_idx = np.argsort(mean_shap)[::-1]
        
        # Prepare data for plotting
        sorted_features = [self.feature_names[i] for i in sorted_idx]
        shap_sorted = self.shap_values[:, sorted_idx]
        X_sorted = X_sample[:, sorted_idx]
        
        fig = go.Figure()
        
        # Create scatter plot for each feature
        for i, feature in enumerate(sorted_features):
            # Add jitter for better visualization
            y_pos = np.ones(X_sorted.shape[0]) * i
            jitter = np.random.normal(0, 0.08, X_sorted.shape[0])
            y_jittered = y_pos + jitter
            
            fig.add_trace(go.Scatter(
                x=shap_sorted[:, i],
                y=y_jittered,
                mode='markers',
                name=feature,
                marker=dict(
                    size=6,
                    color=X_sorted[:, i],
                    colorscale='RdYlBu_r',
                    showscale=False,
                    opacity=0.6,
                    line=dict(width=0.5, color='white')
                ),
                text=[f'Feature: {feature}<br>SHAP: {s:.4f}<br>Value: {v:.3f}' 
                      for s, v in zip(shap_sorted[:, i], X_sorted[:, i])],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            ))
        
        fig.update_layout(
            title=dict(
                text='<b>📊 SHAP Feature Importance - Model Predictions</b><br><sub>Interactive beeswarm plot showing feature impacts</sub>',
                x=0.5,
                font=dict(size=16, family='Arial Black')
            ),
            xaxis=dict(
                title='SHAP Value (Impact on Model Output)',
                showgrid=True,
                gridcolor='lightgray',
                zeroline=True,
                zerolinecolor='red',
                zerolinewidth=1
            ),
            yaxis=dict(
                title='Features',
                tickvals=list(range(len(sorted_features))),
                ticktext=sorted_features,
                showgrid=False
            ),
            height=700,
            width=1000,
            template='plotly_white',
            hovermode='closest'
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(str(save_path).replace('.html', '.png'), width=1000, height=700)
            print(f"✅ Saved to {save_path}")
        
        return fig
    
    def create_animated_bar_plot(self, X_sample: np.ndarray,
                                  save_path: Optional[Path] = None) -> go.Figure:
        """
        Create animated SHAP bar plot (mean absolute SHAP values)
        
        Args:
            X_sample: Sample data for plotting
            save_path: Path to save the plot (optional)
        
        Returns:
            Plotly figure object
        """
        print("\n📊 Creating animated SHAP bar plot...")
        
        # Calculate mean absolute SHAP values
        mean_shap = np.abs(self.shap_values).mean(axis=0)
        
        # Sort by importance
        sorted_idx = np.argsort(mean_shap)
        features_sorted = [self.feature_names[i] for i in sorted_idx]
        importance_sorted = mean_shap[sorted_idx]
        
        # Calculate cumulative importance
        cumulative = np.cumsum(importance_sorted) / np.sum(importance_sorted) * 100
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Mean |SHAP| Values', 'Cumulative Importance (%)'),
            column_widths=[0.6, 0.4],
            specs=[[{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Bar chart
        fig.add_trace(
            go.Bar(
                x=importance_sorted,
                y=features_sorted,
                orientation='h',
                marker=dict(
                    color=importance_sorted,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title='Mean SHAP', x=1.02)
                ),
                text=[f'{val:.4f}' for val in importance_sorted],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Mean SHAP: %{x:.4f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Cumulative line
        fig.add_trace(
            go.Scatter(
                x=cumulative,
                y=features_sorted,
                mode='lines+markers',
                name='Cumulative',
                line=dict(color=COLORS['warning'], width=3),
                marker=dict(size=10, color=COLORS['warning']),
                hovertemplate='<b>%{y}</b><br>Cumulative: %{x:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Add 80% threshold
        fig.add_vline(x=80, line_dash="dash", line_color="red", opacity=0.7, row=1, col=2)
        fig.add_annotation(
            x=82, y=features_sorted[-1], text="80% Threshold",
            showarrow=False, font=dict(size=10, color="red"), row=1, col=2
        )
        
        fig.update_layout(
            title=dict(
                text='<b>📊 Mean |SHAP| - Feature Importance Ranking</b><br><sub>Individual importance with cumulative contribution</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=600,
            width=1200,
            template='plotly_white',
            showlegend=False
        )
        
        fig.update_xaxes(title_text='Mean |SHAP|', row=1, col=1)
        fig.update_yaxes(title_text='Features', row=1, col=1)
        fig.update_xaxes(title_text='Cumulative Importance (%)', row=1, col=2, range=[0, 100])
        fig.update_yaxes(title_text='Features', row=1, col=2, matches='y')
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(str(save_path).replace('.html', '.png'), width=1200, height=600)
            print(f"✅ Saved to {save_path}")
        
        return fig
    
    def create_waterfall_plot(self, sample_idx: int, X_sample: np.ndarray,
                               save_path: Optional[Path] = None) -> go.Figure:
        """
        Create waterfall plot for individual prediction
        
        Args:
            sample_idx: Index of sample to explain
            X_sample: Sample data
            save_path: Path to save the plot (optional)
        
        Returns:
            Plotly figure object
        """
        print(f"\n📊 Creating waterfall plot for sample {sample_idx}...")
        
        # Get SHAP values for the specific sample
        shap_sample = self.shap_values[sample_idx]
        
        # Sort by absolute SHAP value
        sorted_idx = np.argsort(np.abs(shap_sample))[::-1][:10]  # Top 10 features
        sorted_features = [self.feature_names[i] for i in sorted_idx]
        sorted_shap = shap_sample[sorted_idx]
        sorted_values = X_sample[sample_idx, sorted_idx]
        
        # Create waterfall chart
        base_value = self.expected_value if not isinstance(self.expected_value, np.ndarray) else self.expected_value[0]
        
        fig = go.Figure(go.Waterfall(
            name="SHAP Contributions",
            orientation="v",
            measure=["absolute"] + ["relative"] * len(sorted_shap) + ["total"],
            x=["Base Value"] + sorted_features + ["Prediction"],
            y=[base_value] + list(sorted_shap) + [base_value + np.sum(sorted_shap)],
            text=[f'{v:.4f}' for v in [base_value] + list(sorted_shap) + [base_value + np.sum(sorted_shap)]],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": COLORS['shap_positive']}},
            decreasing={"marker": {"color": COLORS['shap_negative']}},
            totals={"marker": {"color": COLORS['success']}}
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>🔍 SHAP Waterfall Plot - Sample {sample_idx}</b><br><sub>Feature contributions pushing prediction from base value</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            yaxis=dict(title='SHAP Value (Impact on Prediction)'),
            height=500,
            width=1100,
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(str(save_path).replace('.html', '.png'), width=1100, height=500)
            print(f"✅ Saved to {save_path}")
        
        return fig
    
    def create_3d_interaction_plot(self, feature1_idx: int, feature2_idx: int,
                                    X_sample: np.ndarray,
                                    save_path: Optional[Path] = None) -> go.Figure:
        """
        Create 3D SHAP interaction plot between two features
        
        Args:
            feature1_idx: Index of first feature
            feature2_idx: Index of second feature
            X_sample: Sample data
            save_path: Path to save the plot (optional)
        
        Returns:
            Plotly figure object
        """
        feature1_name = self.feature_names[feature1_idx]
        feature2_name = self.feature_names[feature2_idx]
        print(f"\n📊 Creating 3D interaction plot for {feature1_name} vs {feature2_name}...")
        
        # Extract data
        f1_values = X_sample[:, feature1_idx]
        f2_values = X_sample[:, feature2_idx]
        shap_f1 = self.shap_values[:, feature1_idx]
        
        fig = go.Figure(data=[go.Scatter3d(
            x=f1_values,
            y=f2_values,
            z=shap_f1,
            mode='markers',
            marker=dict(
                size=5,
                color=shap_f1,
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title='SHAP Value'),
                opacity=0.7
            ),
            hovertemplate=f'<b>{feature1_name}:</b> %{{x:.3f}}<br>' +
                          f'<b>{feature2_name}:</b> %{{y:.3f}}<br>' +
                          f'<b>SHAP Value:</b> %{{z:.4f}}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text=f'<b>🎯 3D SHAP Interaction Analysis</b><br><sub>{feature1_name} vs {feature2_name} interaction effects</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title=feature1_name,
                yaxis_title=feature2_name,
                zaxis_title='SHAP Value',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=700,
            width=1000,
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(str(save_path).replace('.html', '.png'), width=1000, height=700)
            print(f"✅ Saved to {save_path}")
        
        return fig
    
    def create_dependence_plot(self, feature_idx: int, X_sample: np.ndarray,
                                interaction_idx: Optional[int] = None,
                                save_path: Optional[Path] = None) -> go.Figure:
        """
        Create SHAP dependence plot with interaction coloring
        
        Args:
            feature_idx: Index of feature to analyze
            X_sample: Sample data
            interaction_idx: Index of interaction feature (optional)
            save_path: Path to save the plot (optional)
        
        Returns:
            Plotly figure object
        """
        feature_name = self.feature_names[feature_idx]
        print(f"\n📊 Creating dependence plot for {feature_name}...")
        
        f_values = X_sample[:, feature_idx]
        shap_f = self.shap_values[:, feature_idx]
        
        # Determine interaction coloring
        if interaction_idx is not None:
            interaction_name = self.feature_names[interaction_idx]
            interaction_values = X_sample[:, interaction_idx]
            colorscale = 'Viridis'
            colorbar_title = interaction_name
        else:
            # Use SHAP value itself for coloring
            interaction_values = shap_f
            colorscale = 'RdYlBu_r'
            colorbar_title = 'SHAP Value'
        
        fig = go.Figure(data=[go.Scatter(
            x=f_values,
            y=shap_f,
            mode='markers',
            marker=dict(
                size=8,
                color=interaction_values,
                colorscale=colorscale,
                showscale=True,
                colorbar=dict(title=colorbar_title),
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            hovertemplate=f'<b>{feature_name}:</b> %{{x:.3f}}<br>' +
                          f'<b>SHAP Value:</b> %{{y:.4f}}<br>' +
                          f'<b>{colorbar_title}:</b> %{{marker.color:.3f}}<extra></extra>'
        )])
        
        # Add trend line (polynomial fit)
        z = np.polyfit(f_values, shap_f, 2)
        p = np.poly1d(z)
        x_trend = np.linspace(f_values.min(), f_values.max(), 100)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend (Quadratic)',
            line=dict(color=COLORS['warning'], width=2, dash='dash')
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>📈 SHAP Dependence Plot</b><br><sub>{feature_name} impact on predictions</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis=dict(title=feature_name),
            yaxis=dict(title='SHAP Value'),
            height=600,
            width=900,
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(str(save_path).replace('.html', '.png'), width=900, height=600)
            print(f"✅ Saved to {save_path}")
        
        return fig
    
    def create_force_plot_html(self, sample_idx: int, X_sample: np.ndarray,
                                save_path: Optional[Path] = None) -> str:
        """
        Create SHAP force plot as HTML (using shap's built-in visualization)
        
        Args:
            sample_idx: Index of sample to explain
            X_sample: Sample data
            save_path: Path to save the HTML
        
        Returns:
            HTML string
        """
        print(f"\n📊 Creating force plot for sample {sample_idx}...")
        
        # Use shap's built-in force plot
        shap.initjs()
        
        # Create force plot
        if len(self.shap_values.shape) == 2:
            force_plot = shap.force_plot(
                self.expected_value,
                self.shap_values[sample_idx, :],
                X_sample[sample_idx, :],
                feature_names=self.feature_names,
                matplotlib=False,
                show=False
            )
        else:
            force_plot = shap.force_plot(
                self.expected_value,
                self.shap_values[sample_idx, :, :],
                X_sample[sample_idx, :],
                feature_names=self.feature_names,
                matplotlib=False,
                show=False
            )
        
        # Save to HTML
        if save_path:
            shap.save_html(str(save_path), force_plot)
            print(f"✅ Saved to {save_path}")
        
        return force_plot
    
    def get_feature_importance_df(self) -> pd.DataFrame:
        """
        Get feature importance based on mean absolute SHAP values
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated. Run create_explainer first.")
        
        mean_shap = np.abs(self.shap_values).mean(axis=0)
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': mean_shap
        }).sort_values('importance', ascending=False)
        
        return importance_df


def create_shap_dashboard(model, X_sample: np.ndarray, feature_names: List[str],
                          save_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Create complete SHAP analysis dashboard
    
    Args:
        model: Trained ML model
        X_sample: Sample data
        feature_names: List of feature names
        save_dir: Directory to save outputs
    
    Returns:
        Dictionary with all figures and data
    """
    print("\n" + "="*60)
    print("🎨 Creating Complete SHAP Analysis Dashboard")
    print("="*60)
    
    # Initialize analyzer
    analyzer = AnimatedSHAPAnalyzer(model, feature_names)
    analyzer.create_explainer(X_sample)
    
    # Set save directory
    if save_dir is None:
        save_dir = SHAP_PATH
    
    save_dir.mkdir(parents=True, exist_ok=True)
    html_dir = save_dir / 'html'
    html_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # 1. Summary plot
    results['summary'] = analyzer.create_animated_summary_plot(
        X_sample, save_path=html_dir / 'shap_summary.html'
    )
    
    # 2. Bar plot
    results['bar'] = analyzer.create_animated_bar_plot(
        X_sample, save_path=html_dir / 'shap_bar.html'
    )
    
    # 3. Feature importance DataFrame
    results['importance_df'] = analyzer.get_feature_importance_df()
    results['importance_df'].to_csv(save_dir / 'feature_importance.csv', index=False)
    
    # 4. Waterfall plot for first sample
    results['waterfall'] = analyzer.create_waterfall_plot(
        0, X_sample, save_path=html_dir / 'shap_waterfall.html'
    )
    
    # 5. 3D interaction plot for top 2 features
    top_features = results['importance_df']['feature'].values[:2]
    top_indices = [feature_names.index(f) for f in top_features]
    
    results['interaction_3d'] = analyzer.create_3d_interaction_plot(
        top_indices[0], top_indices[1], X_sample,
        save_path=html_dir / 'shap_3d_interaction.html'
    )
    
    # 6. Dependence plots for top 3 features
    results['dependence'] = []
    for i, feature in enumerate(results['importance_df']['feature'].values[:3]):
        idx = feature_names.index(feature)
        dep_fig = analyzer.create_dependence_plot(
            idx, X_sample,
            save_path=html_dir / f'shap_dependence_{feature}.html'
        )
        results['dependence'].append(dep_fig)
    
    # 7. Force plot
    results['force_plot'] = analyzer.create_force_plot_html(
        0, X_sample, save_path=html_dir / 'shap_force.html'
    )
    
    print("\n" + "="*60)
    print("✅ SHAP Analysis Dashboard Complete!")
    print("="*60)
    
    print(f"\n📁 Output Directory: {save_dir}")
    print("   HTML Files (Interactive):")
    print("   • shap_summary.html - Beeswarm summary plot")
    print("   • shap_bar.html - Mean SHAP bar chart")
    print("   • shap_waterfall.html - Individual prediction explanation")
    print("   • shap_3d_interaction.html - 3D interaction analysis")
    print("   • shap_dependence_*.html - Feature dependence plots")
    print("   • shap_force.html - Force plot visualization")
    print("\n   Data Files:")
    print("   • feature_importance.csv - Importance rankings")
    
    return results


# Convenience functions
def plot_shap_summary(model, X_sample: np.ndarray, feature_names: List[str],
                      save_path: Optional[Path] = None) -> go.Figure:
    """Convenience function to plot SHAP summary"""
    analyzer = AnimatedSHAPAnalyzer(model, feature_names)
    analyzer.create_explainer(X_sample)
    return analyzer.create_animated_summary_plot(X_sample, save_path)


def plot_shap_bar(model, X_sample: np.ndarray, feature_names: List[str],
                  save_path: Optional[Path] = None) -> go.Figure:
    """Convenience function to plot SHAP bar chart"""
    analyzer = AnimatedSHAPAnalyzer(model, feature_names)
    analyzer.create_explainer(X_sample)
    return analyzer.create_animated_bar_plot(X_sample, save_path)


def plot_shap_waterfall(model, X_sample: np.ndarray, feature_names: List[str],
                        sample_idx: int = 0, save_path: Optional[Path] = None) -> go.Figure:
    """Convenience function to plot SHAP waterfall"""
    analyzer = AnimatedSHAPAnalyzer(model, feature_names)
    analyzer.create_explainer(X_sample)
    return analyzer.create_waterfall_plot(sample_idx, X_sample, save_path)


if __name__ == "__main__":
    # Example usage with sample data
    print("="*60)
    print("🎨 SHAP Analysis Example")
    print("="*60)
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 15
    
    X_sample = np.random.randn(n_samples, n_features)
    feature_names = [f'feature_{i}' for i in range(n_features)]
    
    # Create a simple model for demonstration
    from sklearn.ensemble import RandomForestRegressor
    
    # Generate synthetic target
    y = X_sample @ np.random.randn(n_features) + np.random.randn(n_samples) * 0.1
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_sample, y)
    
    # Run SHAP analysis
    results = create_shap_dashboard(model, X_sample[:200], feature_names)
    
    print("\n📊 Top 5 Feature Importance:")
    print(results['importance_df'].head())
    
    print("\n💡 To view interactive plots, open the HTML files in your browser:")
    print(f"   {SHAP_PATH / 'html' / 'shap_summary.html'}")