"""Initialize monetization database"""
from src.auth.user_manager import UserManager
import os

def init():
    print("Initializing Monetization Infrastructure...")
    um = UserManager()
    
    # Create a demo user
    demo_user = um.create_user("muhammad.aammar.amjad@gmail.com", "battle-hardened-2026")
    if demo_user:
        print(f"DONE: Demo user created: {demo_user['email']}")
        print(f"API Key: {demo_user['api_key']}")
        
        # Upgrade to enterprise for testing
        um.upgrade_tier(demo_user['id'], "enterprise", "sub_demo_123")
        print("Tier upgraded to: ENTERPRISE")
    else:
        print("INFO: Demo user already exists")
    
    print("DONE: Initialization Complete")

if __name__ == "__main__":
    init()
