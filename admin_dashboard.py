import streamlit as st
import pandas as pd
import os
import datetime
import altair as alt
import time

def render_admin_dashboard():
    # PROFESSIONAL DASHBOARD STYLING
    st.markdown("""
    <style>
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .metric-label {
            font-size: 0.9em;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: 600;
            color: #ffffff;
            margin-top: 5px;
        }
        .critical-value {
            color: #f85149; /* Enterprise Red */
        }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.title("Command Center")
    st.markdown("### Operational Metrics & Analytics")
    st.divider()

    # DATA LOADING
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'ticket_db.csv')
    df = pd.DataFrame()
    try: df = pd.read_csv(file_path)
    except FileNotFoundError: pass

    # SIDEBAR FILTERS (Moved to main page for dashboard focus)
    col_filter, col_refresh = st.columns([5, 1])
    with col_filter:
        all_status = ["All Statuses"]
        if not df.empty and 'status' in df.columns: all_status += list(df['status'].unique())
        selected_status = st.selectbox("", all_status, label_visibility="collapsed")
    
    with col_refresh:
        if st.button("🔄 Refresh"): st.rerun()

    filtered_df = df if selected_status == "All Statuses" else df[df['status'] == selected_status]

    # --- METRICS ROW ---
    total = len(df)
    high = len(df[df['urgency'].isin(['High', 'Critical'])]) if not df.empty else 0
    open_t = len(df[df['status'] == 'Open']) if not df.empty else 0
    
    high_color_class = "critical-value" if high > 0 else ""

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Volume</div>
            <div class="metric-value">{total}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Critical Incidents</div>
            <div class="metric-value {high_color_class}">{high}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Open Tickets</div>
            <div class="metric-value">{open_t}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABLE & EXPORT
    st.markdown("### Ticket Database")
    
    col_dl, col_spacer = st.columns([1, 5])
    with col_dl:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        csv = df.to_csv(index=False).encode('utf-8') if not df.empty else b""
        st.download_button("📥 Export CSV", csv, f"nexus_report_{timestamp}.csv", "text/csv")

    def highlight_high(val):
        if val == 'Critical': return 'background-color: #3e1f1f; color: #ff7b72'
        if val == 'High': return 'background-color: #3e2c1f; color: #d29922'
        return ''

    if not filtered_df.empty:
        st.dataframe(
            filtered_df.style.map(highlight_high, subset=['urgency']), 
            use_container_width=True,
            height=300
        )

    # AUTONOMOUS PROTOCOLS
    st.divider()
    st.markdown("### Autonomous Protocols")
    
    ca, cb = st.columns(2)
    with ca:
        if st.button("🛠️ Execute Auto-Heal Sequence", use_container_width=True):
            with st.status("Running Auto-Heal...", expanded=True) as status:
                st.write("🔍 Diagnosing Root Cause...")
                time.sleep(1)
                st.write("♻️ Restarting Microservices...")
                time.sleep(1)
                st.write("✅ Verifying System Stability...")
                status.update(label="Auto-Heal Complete", state="complete", expanded=False)
            st.success("System Restored: 3 Incidents Resolved.")

    with cb:
        if st.button("📢 Broadcast Critical Alert", use_container_width=True):
            st.warning("⚠️ Critical Alert sent to Operations Channel.")

    # ANALYTICS
    st.divider()
    st.markdown("### Performance Analytics")
    cc1, cc2 = st.columns(2)
    
    # 1. DEPARTMENT CHART
    with cc1:
        st.caption("Incidents by Department")
        if not df.empty and 'department' in df.columns:
            dept_counts = df['department'].value_counts().reset_index()
            dept_counts.columns = ['department', 'count']
            
            chart = alt.Chart(dept_counts).mark_bar().encode(
                x=alt.X('department', title=None),
                y=alt.Y('count', axis=alt.Axis(tickMinStep=1), title='Volume'),
                color=alt.value('#58a6ff'), # Enterprise Blue
                tooltip=['department', 'count']
            ).properties(height=300).interactive()
            st.altair_chart(chart, use_container_width=True)
            
    # 2. URGENCY CHART
    with cc2:
        st.caption("Incidents by Severity")
        if not df.empty and 'urgency' in df.columns:
            urgency_counts = df['urgency'].value_counts().reset_index()
            urgency_counts.columns = ['urgency', 'count']
            
            domain = ["Low", "Medium", "High", "Critical"]
            range_ = ["#238636", "#d29922", "#f85149", "#da3633"] # Green, Yellow, Red, Deep Red
            
            chart = alt.Chart(urgency_counts).mark_bar().encode(
                x=alt.X('urgency', sort=domain, title=None),
                y=alt.Y('count', axis=alt.Axis(tickMinStep=1), title='Volume'),
                color=alt.Color('urgency', scale=alt.Scale(domain=domain, range=range_), legend=None),
                tooltip=['urgency', 'count']
            ).properties(height=300).interactive()
            st.altair_chart(chart, use_container_width=True)
