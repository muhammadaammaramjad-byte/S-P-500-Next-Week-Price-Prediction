"""Automated email marketing for conversion"""
import os
from datetime import datetime
from typing import Optional

# Mock SendGrid for illustration if key not provided
class MockSendGrid:
    def send(self, message):
        print(f"DEBUG: Sending email to {message['to']} with subject '{message['subject']}'")
        return True

class EmailMarketing:
    """Automated email sequences for leads and customers"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        if self.api_key:
            # import sendgrid
            # self.sg = sendgrid.SendGridAPIClient(self.api_key)
            self.sg = MockSendGrid()
        else:
            self.sg = MockSendGrid()
    
    def send_welcome_email(self, email: str, tier: str = "free"):
        """Welcome sequence"""
        content = f"""
        Welcome to S&P 500 Predictor!
        
        You've joined {tier} tier.
        
        Quick start:
        1. Visit dashboard.sp500predictor.com
        2. Start making profitable trades!
        
        Need help? Reply to this email.
        """
        
        message = {
            'to': email,
            'subject': f'Welcome to S&P 500 Predictor - {tier.capitalize()} Tier',
            'content': content
        }
        self.sg.send(message)
    
    def send_upgrade_reminder(self, email: str, current_tier: str):
        """Nudge free users to upgrade"""
        benefits = {
            "individual": "real-time data and 10x more API calls",
            "professional": "custom models and white-label dashboard"
        }
        
        message = {
            'to': email,
            'subject': f'Unlock {benefits.get(current_tier, "more features")} - Upgrade Now',
            'content': "Your trading edge is waiting..."
        }
        self.sg.send(message)
    
    def send_churn_prevention(self, email: str):
        """Prevent cancellation with special offer"""
        message = {
            'to': email,
            'subject': "Don't go! Here's 30% off your next month",
            'content': "We value you as a customer..."
        }
        self.sg.send(message)
