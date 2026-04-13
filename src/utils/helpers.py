import time
import functools
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

def get_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now().strftime(format_str)

def ensure_directory(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def format_percentage(value: float, decimals: int = 2) -> str:
    return f"{value * 100:.{decimals}f}%"

def format_currency(value: float) -> str:
    return f"${value:,.2f}"
