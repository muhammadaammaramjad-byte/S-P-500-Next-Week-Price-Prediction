"""User management with tier-based access"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
from pathlib import Path

class UserManager:
    """Handle user accounts, API keys, and access control"""
    
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    stripe_customer_id TEXT,
                    tier TEXT DEFAULT 'free',
                    subscription_status TEXT DEFAULT 'inactive',
                    subscription_end DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    api_key TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    tier TEXT,
                    stripe_session_id TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def create_user(self, email: str, password: str) -> Optional[Dict]:
        """Create new user account"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        api_key = secrets.token_urlsafe(32)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO users (email, password_hash, api_key) VALUES (?, ?, ?)",
                    (email, password_hash, api_key)
                )
                user_id = cursor.lastrowid
                
                return {
                    "id": user_id,
                    "email": email,
                    "api_key": api_key,
                    "tier": "free"
                }
        except sqlite3.IntegrityError:
            return None
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, email, tier, subscription_status, api_key FROM users WHERE email=? AND password_hash=?",
                (email, password_hash)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    "id": user[0],
                    "email": user[1],
                    "tier": user[2],
                    "subscription_status": user[3],
                    "api_key": user[4]
                }
        return None
    
    def check_access(self, api_key: str, required_tier: str) -> bool:
        """Check if user has access to feature"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT tier, subscription_status FROM users WHERE api_key=?",
                (api_key,)
            )
            user = cursor.fetchone()
            
            if not user:
                return False
            
            user_tier = user[0]
            status = user[1]
            
            # Tier hierarchy
            tier_levels = {"free": 0, "individual": 1, "professional": 2, "enterprise": 3}
            
            return (status == "active" and 
                    tier_levels.get(user_tier, 0) >= tier_levels.get(required_tier, 0))
    
    def upgrade_tier(self, user_id: int, tier: str, stripe_session_id: str):
        """Upgrade user to paid tier"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET tier=?, subscription_status='active', subscription_end=DATE('now', '+1 month') WHERE id=?",
                (tier, user_id)
            )
            # Tier prices are in dollars, payments table expects amount (cents usually)
            # Importing PaymentManager here to avoid circular imports if needed, but here it's fine
            from src.payments.stripe_client import PaymentManager
            conn.execute(
                "INSERT INTO payments (user_id, amount, tier, stripe_session_id, status) VALUES (?, ?, ?, ?, 'completed')",
                (user_id, PaymentManager.TIER_PRICES[tier]["monthly"] * 100, tier, stripe_session_id)
            )
    
    def log_api_usage(self, api_key: str, endpoint: str):
        """Track API usage for billing"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO api_usage (api_key, endpoint) VALUES (?, ?)",
                (api_key, endpoint)
            )
    
    def get_api_usage(self, api_key: str, days: int = 30) -> int:
        """Get API call count for period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM api_usage WHERE api_key=? AND timestamp > DATE('now', ?)",
                (api_key, f"-{days} days")
            )
            return cursor.fetchone()[0]
