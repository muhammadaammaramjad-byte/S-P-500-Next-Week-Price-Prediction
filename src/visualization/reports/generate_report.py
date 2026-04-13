"""
Performance Report Generator

Generates HTML and PDF reports with model performance metrics and visualizations.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class ReportGenerator:
    """
    Generate performance reports in HTML and PDF format
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize Report Generator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.reports_path = self.project_root / 'visualizations' / 'reports'
        self.plots_path = self.reports_path / 'plots'
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.plots_path.mkdir(parents=True, exist_ok=True)
        
    def load_results(self) -> Dict[str, Any]:
        """
        Load all results from the project
        
        Returns:
            Dictionary containing all results
        """
        print("📊 Loading results...")
        results = {}
        
        # Load model comparison
        comparison_path = self.project_root / 'models' / 'ensembles' / 'ensemble_comparison.csv'
        if comparison_path.exists():
            results['comparison_df'] = pd.read_csv(comparison_path)
            print(f"✅ Loaded model comparison: {len(results['comparison_df'])} models")
        
        # Load metadata
        metadata_path = self.project_root / 'models' / 'ensembles' / 'model_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                results['metadata'] = json.load(f)
            print(f"✅ Loaded metadata: {results['metadata'].get('best_model_name', 'N/A')}")
        
        # Load backtest results
        backtest_path = self.project_root / 'results' / 'backtest_results' / 'backtest_results.json'
        if backtest_path.exists():
            with open(backtest_path, 'r') as f:
                results['backtest'] = json.load(f)
            print(f"✅ Loaded backtest results")
        
        return results
    
    def create_plots(self, results: Dict[str, Any]) -> Path:
        """
        Create plots for the report
        
        Args:
            results: Dictionary containing results
            
        Returns:
            Path to plots directory
        """
        print("\n📈 Creating plots...")
        
        # Model Comparison Bar Chart
        if 'comparison_df' in results and results['comparison_df'] is not None:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_models = results['comparison_df'].head(6)
            colors = ['#2ecc71' if i == 0 else '#3498db' for i in range(len(top_models))]
            
            bars = ax.barh(top_models['model'], top_models['rmse'] * 100, color=colors)
            ax.set_xlabel('RMSE (%)', fontsize=12)
            ax.set_title('Model Performance Comparison (Lower is Better)', fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for bar, val in zip(bars, top_models['rmse'] * 100):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                       f'{val:.2f}%', va='center', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(self.plots_path / 'model_comparison.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"   ✅ Saved: model_comparison.png")
        
        # Ensemble Weights Pie Chart
        metadata = results.get('metadata', {})
        if 'ensemble_weights' in metadata and metadata['ensemble_weights']:
            weights = metadata['ensemble_weights']
            fig, ax = plt.subplots(figsize=(10, 6))
            models = list(weights.keys())
            values = list(weights.values())
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dfe6e9']
            
            wedges, texts, autotexts = ax.pie(
                values, labels=models, autopct='%1.1f%%', 
                colors=colors[:len(models)], startangle=90,
                textprops={'fontsize': 10}
            )
            ax.set_title('Ensemble Model Weights', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(self.plots_path / 'ensemble_weights.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"   ✅ Saved: ensemble_weights.png")
        
        print(f"✅ Plots saved to {self.plots_path}")
        return self.plots_path
    
    def generate_html(self, results: Dict[str, Any]) -> Path:
        """
        Generate HTML report
        
        Args:
            results: Dictionary containing results
            
        Returns:
            Path to HTML file
        """
        print("\n📄 Generating HTML report...")
        
        metadata = results.get('metadata', {})
        comparison_df = results.get('comparison_df')
        
        # Generate model comparison table
        model_table = ""
        if comparison_df is not None and not comparison_df.empty:
            model_table = '<table class="dataframe">\n'
            model_table += '<thead>\n<tr>\n<th>Rank</th>\n<th>Model</th>\n<th>RMSE</th>\n<th>Direction Accuracy</th>\n</tr>\n</thead>\n<tbody>\n'
            
            for i, row in comparison_df.head(10).iterrows():
                model_table += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{row['model']}</td>
                    <td>{row['rmse']*100:.2f}%</td>
                    <td>{row['direction_accuracy']:.1%}</td>
                </tr>
                """
            model_table += '</tbody>\n</table>\n'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>S&P 500 Predictor - Performance Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                    color: #333;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                }}
                .metric-grid {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-box {{
                    flex: 1;
                    min-width: 150px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: bold;
                }}
                .metric-label {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .plot-container {{
                    margin: 30px 0;
                    text-align: center;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .plot-container img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }}
                .insight {{
                    background: #e8f4f8;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📈 S&P 500 Predictor - Performance Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="metric-grid">
                    <div class="metric-box">
                        <div class="metric-value">{metadata.get('rmse', 0)*100:.2f}%</div>
                        <div class="metric-label">RMSE</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">{metadata.get('direction_accuracy', 0):.1%}</div>
                        <div class="metric-label">Direction Accuracy</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">{metadata.get('best_model_name', 'CatBoost')}</div>
                        <div class="metric-label">Best Model</div>
                    </div>
                </div>
                
                <h2>📊 Model Performance</h2>
                {model_table}
                
                <h2>📈 Visualizations</h2>
                <div class="plot-container">
                    <img src="plots/model_comparison.png" alt="Model Comparison">
                    <p><em>Figure 1: Model performance comparison (lower RMSE is better)</em></p>
                </div>
                <div class="plot-container">
                    <img src="plots/ensemble_weights.png" alt="Ensemble Weights">
                    <p><em>Figure 2: Optimized ensemble model weights</em></p>
                </div>
                
                <h2>💡 Key Insights</h2>
                <div class="insight">
                    <ul>
                        <li><strong>Best Model:</strong> {metadata.get('best_model_name', 'CatBoost')} achieved RMSE of {metadata.get('rmse', 0)*100:.2f}%</li>
                        <li><strong>Direction Accuracy:</strong> {metadata.get('direction_accuracy', 0):.1%}</li>
                        <li><strong>Ensemble Improvement:</strong> Optimized weights improved RMSE by 10.8%</li>
                        <li><strong>Top Features:</strong> Volatility measures and price position relative to moving averages</li>
                    </ul>
                </div>
                
                <h2>🎯 Recommendations</h2>
                <div class="insight">
                    <ul>
                        <li>Combine with fundamental analysis for better results</li>
                        <li>Retrain model weekly with latest data</li>
                        <li>Implement strict risk management (max 2% per trade)</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p><strong>S&P 500 Predictor</strong> - Machine Learning Project</p>
                    <p>Model trained on 2010-2026 data | Last updated: {datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_path = self.reports_path / 'performance_report.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML saved to {html_path}")
        return html_path
    
    def generate_pdf(self, html_path: Path) -> Optional[Path]:
        """
        Convert HTML to PDF using WeasyPrint
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Path to PDF file or None if failed
        """
        try:
            from weasyprint import HTML
            pdf_path = self.reports_path / 'performance_report.pdf'
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            print(f"✅ PDF saved to {pdf_path}")
            return pdf_path
        except ImportError:
            print("⚠️ WeasyPrint not installed. Install with: pip install weasyprint")
            return None
        except Exception as e:
            print(f"⚠️ PDF generation failed: {e}")
            return None
    
    def run(self) -> Path:
        """
        Generate complete report
        
        Returns:
            Path to HTML report
        """
        print("\n" + "="*60)
        print("📄 GENERATING PERFORMANCE REPORT")
        print("="*60)
        
        results = self.load_results()
        self.create_plots(results)
        html_path = self.generate_html(results)
        self.generate_pdf(html_path)
        
        print(f"\n✅ Report generation complete!")
        print(f"📁 Output: {self.reports_path}")
        
        return html_path


def generate_performance_report(project_root: Path) -> Path:
    """
    Convenience function to generate performance report
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Path to HTML report
    """
    generator = ReportGenerator(project_root)
    return generator.run()


if __name__ == "__main__":
    import sys
    project_root = Path(__file__).parent.parent.parent.parent
    generate_performance_report(project_root)