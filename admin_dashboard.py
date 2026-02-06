import streamlit as st
import pandas as pd
import os
import datetime
import altair as alt
import time

def render_admin_dashboard():
    # CSS FOR METRIC CARDS
    st.markdown("""
    <style>
        .metric-container {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .metric-card {
            background: rgba(0, 20, 30, 0.7);
            border: 1px solid #00f2ff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 242, 255, 0.1);
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(0, 242, 255, 0.5);
            background: rgba(0, 40, 60, 0.8);
            border-color: #fff;
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
            display: block;
        }
        .metric-label {
            font-size: 1.0em;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
        }
        
        /* CRITICAL CARD STYLE */
        .critical-card {
            border-color: #ff4b4b;
            background: rgba(50, 0, 0, 0.6);
            animation: pulse 2s infinite;
        }
        .critical-card .metric-value { color: #ff4b4b; text-shadow: 0 0 15px #ff0000; }
        .critical-card:hover { box-shadow: 0 0 30px #ff0000; }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
        }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    col_logo, col_text = st.columns([1, 10])
    with col_logo: st.markdown("# 🛡️") 
    with col_text:
        st.title("Nexus Command Center")
        st.markdown("*Real-time AI Support Monitoring System*")
    st.divider()

    # DATA LOADING
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'ticket_db.csv')
    df = pd.DataFrame()
    try: df = pd.read_csv(file_path)
    except FileNotFoundError: pass

    # SIDEBAR FILTERS
    st.sidebar.header("🔍 FILTERS")
    all_status = ["All"]
    if not df.empty and 'status' in df.columns: all_status += list(df['status'].unique())
    selected_status = st.sidebar.selectbox("STATUS FILTER", all_status, key="admin_status_filter")
    filtered_df = df if selected_status == "All" else df[df['status'] == selected_status]

    # METRICS HEADER
    col_header, col_btn = st.columns([4,1]) 
    with col_header: st.subheader("📊 LIVE METRICS")
    with col_btn: 
        if st.button("🔄 REFRESH"): st.rerun()

    # --- CUSTOM HTML CARDS FOR METRICS ---
    total = len(df)
    high = len(df[df['urgency'].isin(['High', 'Critical'])]) if not df.empty else 0
    open_t = len(df[df['status'] == 'Open']) if not df.empty else 0
    
    # CSS Classes for styling
    high_class = "critical-card" if high > 0 else "metric-card"
    high_icon = "🔥" if high > 0 else "✅"

    cols = st.columns(3)
    
    # CARD 1: TOTAL
    cols[0].markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📂</span>
            <div class="metric-label">Total Tickets</div>
            <div class="metric-value">{total}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # CARD 2: HIGH PRIORITY (Becomes Red if > 0)
    cols[1].markdown(f"""
        <div class="metric-card {high_class}">
            <span class="metric-icon">{high_icon}</span>
            <div class="metric-label">Critical Issues</div>
            <div class="metric-value">{high}</div>
        </div>
    """, unsafe_allow_html=True)

    # CARD 3: OPEN
    cols[2].markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🔓</span>
            <div class="metric-label">Open Tickets</div>
            <div class="metric-value">{open_t}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABLE & EXPORT
    st.markdown("---")
    c1, c2 = st.columns([6, 2])
    with c1: st.subheader("DATABASE LOGS")
    with c2:
        timestamp = datetime.datetime.now().strftime("%H-%M")
        csv = df.to_csv(index=False).encode('utf-8') if not df.empty else b""
        st.download_button("📥 EXPORT REPORT", csv, f"nexus_{timestamp}.csv", "text/csv")

    def highlight_high(val):
        return 'background-color: #3d0000; color: #ff4b4b; font-weight: bold; border: 1px solid red' if val in ['Critical', 'High'] else ''

    if not filtered_df.empty:
        st.dataframe(filtered_df.style.map(highlight_high, subset=['urgency']), use_container_width=True)

    # ==========================================
    # 6. AUTONOMOUS ACTIONS (REPLACES JIRA INTEGRATION)
    # ==========================================
    st.markdown("---")
    st.subheader("⚡ AUTONOMOUS PROTOCOLS")
    
    ca, cb = st.columns(2)
    
    with ca:
        # THE "SELF-HEALING" BUTTON
        if st.button("🛠️ EXECUTE AUTO-HEAL PROTOCOLS", use_container_width=True):
            placeholder = st.empty()
            bar = st.progress(0)
            
            # Simulation Steps
            steps = [
                "🔍 DIAGNOSING ROOT CAUSE...",
                "🛡️ ISOLATING AFFECTED NODES...",
                "♻️ RESTARTING MICROSERVICES...",
                "✅ VERIFYING SYSTEM STABILITY..."
            ]
            
            for i, step in enumerate(steps):
                placeholder.markdown(f"**{step}**")
                # Smooth progress bar animation
                for p in range(25):
                    time.sleep(0.015) 
                    bar.progress((i * 25) + p)
            
            bar.progress(100)
            placeholder.success("✅ SYSTEM RESTORED: 3 Low-Priority Incidents Resolved.")
            st.toast("Auto-Heal Complete", icon="⚡")

    with cb:
        # THE "BROADCAST" BUTTON
        if st.button("📢 BROADCAST MAJOR INCIDENT ALERT", use_container_width=True):
            with st.spinner("📡 SENDING ENCRYPTED ALERTS TO ALL STAKEHOLDERS..."):
                time.sleep(1.5)
            st.error("🚨 ALERT BROADCAST SENT: OPS TEAM DEPLOYED.")
            st.toast("Alert Sent", icon="🚨")

    # ==========================================
    # 7. ANALYTICS CHARTS (GHOST THEME)
    # ==========================================
    st.markdown("---")
    st.subheader("ANALYTICS 📈")
    cc1, cc2 = st.columns(2)
    
    # 1. DEPARTMENT CHART
    with cc1:
        st.write("**By Department**")
        if not df.empty and 'department' in df.columns:
            dept_counts = df['department'].value_counts().reset_index()
            dept_counts.columns = ['department', 'count']
            
            # STYLED TRANSPARENT CHART
            dept_chart = alt.Chart(dept_counts).mark_bar().encode(
                x=alt.X('department', sort='-y', title=None),
                y=alt.Y('count', axis=alt.Axis(tickMinStep=1), title='Count'),
                color=alt.value('#00d4ff'), # Neon Cyan Bars
                tooltip=['department', 'count']
            ).properties(
                background='transparent' # <--- REMOVES BLACK BOX
            ).configure_axis(
                labelColor='white',
                titleColor='#00d4ff',
                gridColor='#333'
            ).configure_view(
                stroke=None
            ).interactive()
            
            st.altair_chart(dept_chart, use_container_width=True)
            
    # 2. URGENCY CHART
    with cc2:
        st.write("**By Urgency**")
        if not df.empty and 'urgency' in df.columns:
            urgency_counts = df['urgency'].value_counts().reset_index()
            urgency_counts.columns = ['urgency', 'count']
            
            domain = ["Low", "Medium", "High", "Critical"]
            range_ = ["#00CC96", "#FFA500", "#FF4B4B", "#8B0000"]
            
            urgency_chart = alt.Chart(urgency_counts).mark_bar().encode(
                x=alt.X('urgency', sort=domain, title=None),
                y=alt.Y('count', axis=alt.Axis(tickMinStep=1), title='Count'),
                color=alt.Color('urgency', scale=alt.Scale(domain=domain, range=range_), legend=None),
                tooltip=['urgency', 'count']
            ).properties(
                background='transparent' # <--- REMOVES BLACK BOX
            ).configure_axis(
                labelColor='white',
                titleColor='#00d4ff',
                gridColor='#333'
            ).configure_view(
                stroke=None
            ).interactive()
            
            st.altair_chart(urgency_chart, use_container_width=True)
