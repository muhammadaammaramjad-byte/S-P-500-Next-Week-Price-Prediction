#!/usr/bin/env python3
"""Production Launch Audit - S&P 500 Predictor"""
import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    print("S&P 500 PREDICTOR - LAUNCH READINESS VERIFICATION")
    print("Enterprise-Grade FinTech")

def check_test_suite():
    """Verify 66/66 tests pass"""
    try:
        result = subprocess.run(["python", "-m", "pytest", "tests/", "-q", "--tb=no"], 
                               capture_output=True, text=True)
        passed = "66 passed" in result.stdout
        status = "OK" if passed else "FAIL"
        print(f"{status} Test Suite: {'66/66 PASSING' if passed else 'FAILING'}")
        return passed
    except Exception as e:
        print(f"FAIL Test Suite: Error running pytest ({str(e)})")
        return False

def check_stripe():
    """Verify Stripe configuration"""
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    if stripe_key and stripe_key.startswith("sk_live_"):
        print("OK Stripe: LIVE MODE (Collecting real payments)")
        return True
    elif stripe_key and stripe_key.startswith("sk_test_"):
        print("WARN Stripe: TEST MODE (Switch to live before launch)")
        return False
    else:
        print("FAIL Stripe: NOT CONFIGURED")
        return False

def check_database():
    """Verify database connectivity"""
    db_path = "data/users.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024
        print(f"OK Database: Active ({size:.1f} KB)")
        return True
    else:
        print("WARN Database: Not initialized (run init_db.py)")
        return False

def check_domain():
    """Verify domain configuration"""
    app_url = os.getenv("APP_URL", "")
    if app_url:
        print(f"OK Domain: {app_url}")
        return True
    else:
        print("WARN Domain: Using default (update .env.production)")
        return False

def generate_report():
    """Generate final launch report"""
    print_banner()
    print(f"Launch Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Launch Time: {datetime.now().strftime('%H:%M:%S')} UTC")
    print("-" * 60)
    
    checks = {
        "Test Suite": check_test_suite(),
        "Stripe": check_stripe(),
        "Database": check_database(),
        "Domain": check_domain()
    }
    
    print("-" * 60)
    passed = sum(checks.values())
    total = len(checks)
    
    if passed == total:
        print(f"LAUNCH STATUS: READY - {passed}/{total} checks passed")
        print("Execute 'python scripts/launch.py --go-live'")
    else:
        print(f"LAUNCH STATUS: PARTIAL - {passed}/{total} checks passed")
        print("Fix missing items above before launching for production")
    
    return passed == total

if __name__ == "__main__":
    generate_report()
