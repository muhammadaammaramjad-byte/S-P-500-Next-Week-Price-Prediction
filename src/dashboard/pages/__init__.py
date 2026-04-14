"""Dashboard pages module"""
try:
    from .launch_tracker import render_launch_tracker
    from .sla_dashboard import render_sla_dashboard
    from .subscription import render_subscription_page, render_account_page
except ImportError:
    # Fallbacks for missing pages or dependencies
    def render_launch_tracker():
        import streamlit as st
        st.info("Launch Tracker initialized...")
        
    def render_sla_dashboard():
        import streamlit as st
        st.info("SLA Dashboard initialized...")
        
    def render_subscription_page():
        import streamlit as st
        st.info("Subscription Page (Limited Access)")
        
    def render_account_page():
        import streamlit as st
        st.info("Account Management initialized...")
