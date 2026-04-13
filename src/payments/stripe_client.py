"""Enterprise payment processing with Stripe"""
import stripe
import os
from typing import Dict, Optional
from datetime import datetime
import streamlit as st

# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")

class PaymentManager:
    """Handle subscriptions, payments, and billing"""
    
    # Tier definitions
    PRICE_IDS = {
        "individual": {
            "monthly": "price_individual_monthly",
            "yearly": "price_individual_yearly"
        },
        "professional": {
            "monthly": "price_professional_monthly",
            "yearly": "price_professional_yearly"
        },
        "enterprise": {
            "custom": "price_enterprise_custom"
        }
    }
    
    TIER_PRICES = {
        "individual": {"monthly": 49, "yearly": 499},
        "professional": {"monthly": 499, "yearly": 4999},
        "enterprise": {"monthly": 4999, "yearly": 49999}
    }
    
    TIER_FEATURES = {
        "individual": [
            "Daily S&P 500 predictions",
            "Email alerts",
            "Web dashboard access",
            "1 month historical data",
            "Basic support"
        ],
        "professional": [
            "Everything in Individual",
            "Real-time API access",
            "WebSocket live feed",
            "5 years historical data",
            "Custom indicators",
            "Priority support (24/7)",
            "Team accounts (up to 5)"
        ],
        "enterprise": [
            "Everything in Professional",
            "White-label dashboard",
            "Dedicated infrastructure",
            "Custom model training",
            "SLA guarantee (99.99%)",
            "Dedicated account manager",
            "Unlimited team members",
            "On-premise deployment option"
        ]
    }
    
    @staticmethod
    def create_checkout_session(customer_email: str, tier: str, interval: str = "monthly") -> str:
        """Create Stripe checkout session"""
        try:
            price_id = PaymentManager.PRICE_IDS[tier][interval]
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=os.getenv("SUCCESS_URL", "https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}"),
                cancel_url=os.getenv("CANCEL_URL", "https://yourdomain.com/cancel"),
                customer_email=customer_email,
                metadata={
                    "tier": tier,
                    "interval": interval
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"Stripe error: {e}")
            return None
    
    @staticmethod
    def get_subscription_status(customer_id: str) -> Dict:
        """Check active subscription status"""
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id, status="active")
            if subscriptions.data:
                sub = subscriptions.data[0]
                return {
                    "active": True,
                    "tier": sub.metadata.get("tier", "individual"),
                    "current_period_end": datetime.fromtimestamp(sub.current_period_end),
                    "cancel_at_period_end": sub.cancel_at_period_end
                }
            return {"active": False, "tier": None}
        except Exception:
            return {"active": False, "tier": None}
    
    @staticmethod
    def create_customer(email: str, name: str = None) -> str:
        """Create Stripe customer"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"source": "sp500_predictor"}
        )
        return customer.id
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel subscription at period end"""
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except Exception:
            return False

# Webhook handler for Stripe events
def handle_stripe_webhook(payload: bytes, sig_header: str):
    """Process Stripe webhook events"""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Grant access to user (Note: defined elsewhere or simplified here)
            # activate_user_subscription(
            #     email=session["customer_email"],
            #     tier=session["metadata"]["tier"]
            # )
            pass
        
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Revoke access
            # deactivate_user_subscription(
            #     customer_id=subscription["customer"]
            # )
            pass
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
