"""Enterprise SLA monitoring dashboard"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_sla_dashboard():
    st.markdown("## Service Level Agreement (SLA) Dashboard")
    
    # SLA targets
    sla_targets = {
        "uptime": 99.99,
        "latency_p99": 200,
        "error_rate": 0.01,
        "response_time": 100
    }
    
    # Current metrics (simulated - replace with real data)
    metrics = {
        "uptime": 99.999,
        "latency_p99": 24,
        "error_rate": 0.001,
        "response_time": 42
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta = metrics["uptime"] - sla_targets["uptime"]
        st.metric("Uptime", f"{metrics['uptime']}%", delta=f"+{delta:.3f}%", delta_color="normal")
        st.progress(metrics["uptime"] / 100)
    
    with col2:
        delta = sla_targets["latency_p99"] - metrics["latency_p99"]
        # Use delta_color="inverse" for metrics where lower is better
        st.metric("P99 Latency", f"{metrics['latency_p99']}ms", delta=f"-{delta}ms", delta_color="inverse")
        st.progress(min(metrics["latency_p99"] / sla_targets["latency_p99"], 1.0))
    
    with col3:
        delta = sla_targets["error_rate"] - metrics["error_rate"]
        # Use delta_color="inverse" for metrics where lower is better
        st.metric("Error Rate", f"{metrics['error_rate']*100:.3f}%", delta=f"-{delta*100:.3f}%", delta_color="inverse")
        st.progress(min(metrics["error_rate"] / sla_targets["error_rate"], 1.0))
    
    with col4:
        st.metric("Current SLA Grade", "A++", delta="Exceeding targets")
        st.progress(1.0) # Solid bar for A++ grade
    
    # Uptime history
    st.markdown("### Uptime History (Last 30 Days)")
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    uptimes = [99.99, 99.99, 99.99, 100, 99.99, 99.98, 99.99, 100, 99.99, 99.99,
               100, 99.99, 99.99, 99.99, 100, 99.99, 99.99, 100, 99.99, 99.99,
               99.99, 100, 99.99, 99.99, 99.99, 100, 99.99, 99.99, 99.99, 100]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=uptimes,
        mode='lines+markers',
        name='Uptime %',
        line=dict(color='#4CAF50', width=2),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.2)'
    ))
    
    # Add SLA target line
    fig.add_hline(y=99.99, line_dash="dash", line_color="red", 
                  annotation_text="SLA Target (99.99%)")
    
    fig.update_layout(
        title="30-Day Uptime Performance",
        yaxis_title="Uptime Percentage",
        yaxis_range=[99.95, 100.01],
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Incident history
    st.markdown("### Incident History")
    
    incidents = [
        {"date": "2024-01-15", "duration": "4m", "cause": "Database connection pool", "resolved": True},
        {"date": "2024-01-08", "duration": "2m", "cause": "Redis cache miss storm", "resolved": True},
        {"date": "2024-01-01", "duration": "1m", "cause": "Deployment rollout", "resolved": True}
    ]
    
    for incident in incidents:
        with st.expander(f"Incident: {incident['date']} - {incident['duration']} outage"):
            st.write(f"**Cause:** {incident['cause']}")
            st.write(f"**Resolution:** Auto-recovered via Kubernetes")
            st.write(f"**Impact:** {incident['duration']} of degraded performance")
            st.success("Resolved")
    
    st.markdown("### SLA Compensation Status")
    st.info("No SLA breaches in the last 30 days. $0 compensation owed.")

if __name__ == "__main__":
    render_sla_dashboard()
