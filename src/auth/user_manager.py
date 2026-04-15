"""User management module for authentication and API key tracking."""
from datetime import datetime
from typing import Optional, Dict


class UserManager:
    """Manages user authentication, API keys, and usage tracking."""

    def __init__(self):
        # In-memory store; swap for Redis/PostgreSQL in production
        self._usage: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # API-key helpers
    # ------------------------------------------------------------------

    def get_api_usage(self, api_key: str) -> int:
        """Return current month's API call count for the given key."""
        return self._usage.get(api_key, 0)

    def increment_usage(self, api_key: str, count: int = 1) -> int:
        """Increment the usage counter and return the new total."""
        self._usage[api_key] = self._usage.get(api_key, 0) + count
        return self._usage[api_key]

    def reset_usage(self, api_key: str) -> None:
        """Reset the usage counter (e.g. on billing cycle rollover)."""
        self._usage[api_key] = 0

    # ------------------------------------------------------------------
    # User helpers
    # ------------------------------------------------------------------

    def create_user(self, email: str, tier: str = "free") -> Dict:
        """Create a placeholder user record."""
        import uuid
        return {
            "email": email,
            "tier": tier,
            "api_key": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "subscription_end": None,
        }

    def get_user(self, email: str) -> Optional[Dict]:
        """Retrieve a user record (stub — override with DB lookup)."""
        # Return None so the dashboard falls through to its default state
        return None

    def update_tier(self, email: str, tier: str) -> bool:
        """Update a user's subscription tier (stub)."""
        return True
