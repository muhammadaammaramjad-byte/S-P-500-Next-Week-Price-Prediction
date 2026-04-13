"""Subscription management page for Streamlit dashboard"""
import streamlit as st
from src.payments.stripe_client import PaymentManager
from src.auth.user_manager import UserManager
from datetime import datetime

def render_subscription_page():
    """Professional pricing and subscription UI"""
    
    st.markdown("## 💰 Choose Your Trading Edge")
    st.markdown("Select the plan that fits your trading style")
    
    # Get current user (from session state)
    user = st.session_state.get('user', None)
    
    # Three-tier pricing cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                    border: 2px solid #e0e0e0; text-align: center; height: 100%;">
            <h3>📊 Individual</h3>
            <h2 style="color: #1E88E5;">${PaymentManager.TIER_PRICES['individual']['monthly']}<small style="font-size: 14px;">/mo</small></h2>
            <p style="color: #666;">Perfect for retail traders</p>
            <hr>
        """, unsafe_allow_html=True)
        
        for feature in PaymentManager.TIER_FEATURES['individual']:
            st.markdown(f"✅ {feature}")
        
        if user and user.get('tier') == 'individual':
            st.success("✅ Current Plan")
        else:
            if st.button("🚀 Get Started", key="individual_btn", use_container_width=True):
                url = PaymentManager.create_checkout_session(
                    st.session_state.get('user_email', 'demo@example.com'),
                    "individual",
                    "monthly"
                )
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', 
                               unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E88E5, #1565C0); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white; height: 100%;">
            <h3>🔥 Professional</h3>
            <h2>${PaymentManager.TIER_PRICES['professional']['monthly']}<small style="font-size: 14px;">/mo</small></h2>
            <p>Most Popular • Best Value</p>
            <hr>
        """, unsafe_allow_html=True)
        
        for feature in PaymentManager.TIER_FEATURES['professional']:
            st.markdown(f"✅ {feature}")
        
        if user and user.get('tier') == 'professional':
            st.success("✅ Current Plan")
        else:
            if st.button("💎 Get Pro", key="professional_btn", use_container_width=True):
                url = PaymentManager.create_checkout_session(
                    st.session_state.get('user_email', 'demo@example.com'),
                    "professional",
                    "monthly"
                )
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', 
                               unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                    border: 2px solid #FFC107; text-align: center; height: 100%;">
            <h3>🏢 Enterprise</h3>
            <h2 style="color: #FFC107;">${PaymentManager.TIER_PRICES['enterprise']['monthly']}<small style="font-size: 14px;">/mo</small></h2>
            <p>For institutions & hedge funds</p>
            <hr>
        """, unsafe_allow_html=True)
        
        for feature in PaymentManager.TIER_FEATURES['enterprise']:
            st.markdown(f"✅ {feature}")
        
        if st.button("📞 Contact Sales", key="enterprise_btn", use_container_width=True):
            st.markdown("""
            <script>window.location.href = "mailto:sales@sp500predictor.com?subject=Enterprise Inquiry";</script>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_account_page():
    """User account management"""
    st.markdown("## 👤 Account Settings")
    
    user = st.session_state.get('user', None)
    if not user:
        st.warning("Please log in to view account")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Subscription Details")
        st.metric("Current Plan", user.get('tier', 'free').capitalize())
        st.metric("API Key", user.get('api_key', 'N/A')[:20] + "...")
        
        if user.get('subscription_end'):
            st.info(f"Next billing date: {user['subscription_end']}")
    
    with col2:
        st.markdown("### 📊 Usage Statistics")
        
        # Get API usage
        um = UserManager()
        usage = um.get_api_usage(user['api_key'])
        
        limits = {
            "free": 100,
            "individual": 1000,
            "professional": 10000,
            "enterprise": 100000
        }
        
        limit = limits.get(user.get('tier', 'free'), 100)
        st.progress(min(usage / limit, 1.0))
        st.caption(f"API calls this month: {usage:,} / {limit:,}")
        
        if st.button("🔄 Regenerate API Key", use_container_width=True):
            st.warning("This will invalidate your old API key")
            # Implement key regeneration logic here if needed
