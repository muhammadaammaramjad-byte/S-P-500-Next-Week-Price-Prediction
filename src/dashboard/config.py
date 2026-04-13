"""Dashboard configuration - enterprise grade"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DashboardConfig:
    """Centralized dashboard configuration"""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    ASSETS_DIR: Path = Path(__file__).parent / "assets"
    
    # Theme
    THEME: Dict[str, Any] = None
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    MAX_POINTS_PER_CHART: int = 1000
    
    # Features
    ENABLE_REFRESH: bool = True
    REFRESH_INTERVAL: int = 60  # seconds
    
    def __post_init__(self):
        # Professional color scheme (Fortune 500 style)
        self.THEME = {
            "primary": "#1E88E5",      # Blue
            "secondary": "#FFC107",     # Gold
            "success": "#4CAF50",       # Green
            "danger": "#E53935",        # Red
            "warning": "#FB8C00",       # Orange
            "info": "#00ACC1",          # Cyan
            "dark": "#263238",          # Dark slate
            "light": "#ECEFF1",         # Light gray
            "background": "#FAFAFA",
            "text": "#1A1A1A"
        }

config = DashboardConfig()
