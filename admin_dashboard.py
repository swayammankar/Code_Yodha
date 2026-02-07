import streamlit as st
import pandas as pd
import os
import datetime
import altair as alt
import time

def render_admin_dashboard():
    # --- ENTERPRISE STYLING ---
    st.markdown("""
    <style>
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .action-box {
            background-color: #0d1117;
            border: 1px solid #30363d;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🛡️ Agent Action Terminal")
    
    # LOAD DATA
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'ticket_db.csv')
    
    if not os.path.exists(file_path):
        st.info("Waiting for tickets...")
        return

    df = pd.read_csv(file_path)

    # --- METRICS ---
    total = len(df)
    critical = len(df[df['urgency'] == 'Critical'])
    open_t = len(df[df['status'] == 'Open'])
    solved = len(df[df['status'] == 'Resolved'])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tickets", total)
    m2.metric("Critical Alerts", critical, delta_color="inverse")
    m3.metric("Pending Queue", open_t)
    m4.metric("Resolved", solved)
    
    st.divider()

    # =========================================================
    # TABS (Updated with "Resolved History")
    # =========================================================
    
    tab_queue, tab_work, tab_history, tab_db = st.tabs(["📥 New Queue", "🛠️ My Workspace", "✅ Resolved History", "💾 Database"])

    # --- TAB 1: QUEUE + ANALYTICS ---
    with tab_queue:
        st.markdown("#### 🚨 Unassigned Tickets")
        open_tickets = df[df['status'] == 'Open']
        
        if not open_tickets.empty:
            st.dataframe(open_tickets[['ticket_id', 'urgency', 'department', 'summary', 'timestamp']], use_container_width=True, hide_index=True)
            
            c1, c2 = st.columns([3, 1])
            with c1:
                ticket_to_claim = st.selectbox("Select Ticket to Claim:", open_tickets['ticket_id'].unique(), key="claim_select")
            with c2:
                st.write("")
                st.write("")
                if st.button("🙋‍♂️ Claim Ticket", use_container_width=True, type="primary"):
                    df.loc[df['ticket_id'] == ticket_to_claim, 'status'] = 'In Progress'
                    df.to_csv(file_path, index=False)
                    st.toast(f"Ticket {ticket_to_claim} Locked!", icon="🔒")
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("🎉 Queue is empty!")

        # ANALYTICS CHARTS
        st.markdown("---")
        st.subheader("📊 Live Analytics")
        g1, g2 = st.columns(2)
        
        with g1:
            st.caption("Incidents by Department")
            if not df.empty:
                dept_counts = df['department'].value_counts().reset_index()
                dept_counts.columns = ['department', 'count']
                chart1 = alt.Chart(dept_counts).mark_bar().encode(
                    x=alt.X('department', title=None),
                    y=alt.Y('count', axis=alt.Axis(tickMinStep=1)),
                    color=alt.value('#58a6ff')
                ).interactive()
                st.altair_chart(chart1, use_container_width=True)
            
        with g2:
            st.caption("Incidents by Urgency")
            if not df.empty:
                urg_counts = df['urgency'].value_counts().reset_index()
                urg_counts.columns = ['urgency', 'count']
                domain = ["Low", "Medium", "High", "Critical"]
                range_ = ["#238636", "#d29922", "#f85149", "#da3633"] 
                chart2 = alt.Chart(urg_counts).mark_bar().encode(
                    x=alt.X('urgency', sort=domain, title=None),
                    y=alt.Y('count', axis=alt.Axis(tickMinStep=1)),
                    color=alt.Color('urgency', scale=alt.Scale(domain=domain, range=range_), legend=None)
                ).interactive()
                st.altair_chart(chart2, use_container_width=True)


    # --- TAB 2: WORKSPACE ---
    with tab_work:
        st.markdown("#### 🔨 My Active Tickets")
        my_tickets = df[df['status'] == 'In Progress']
        
        if not my_tickets.empty:
            st.dataframe(my_tickets[['ticket_id', 'department', 'summary', 'rca_hypothesis']], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            ticket_action_id = st.selectbox("Select Active Ticket:", my_tickets['ticket_id'].unique(), key="work_select")
            
            col_a, col_b = st.columns(2)
            
            # RESOLVE
            with col_a:
                st.markdown("""<div class="action-box">✅ <b>Resolution</b></div>""", unsafe_allow_html=True)
                if st.button("Mark as Resolved", use_container_width=True):
                    df.loc[df['ticket_id'] == ticket_action_id, 'status'] = 'Resolved'
                    df.to_csv(file_path, index=False)
                    st.balloons()
                    st.success(f"Ticket {ticket_action_id} Closed!")
                    time.sleep(1.5)
                    st.rerun()

            # TRANSFER
            with col_b:
                st.markdown("""<div class="action-box">⇄ <b>Transfer Department</b></div>""", unsafe_allow_html=True)
                new_dept = st.selectbox("Move to:", ["Hardware", "Software", "Network", "Access"], label_visibility="collapsed")
                if st.button("Transfer Ticket"):
                    df.loc[df['ticket_id'] == ticket_action_id, 'department'] = new_dept
                    df.loc[df['ticket_id'] == ticket_action_id, 'status'] = 'Open' 
                    df.to_csv(file_path, index=False)
                    st.info(f"Transferred to {new_dept}.")
                    time.sleep(1.5)
                    st.rerun()

        else:
            st.info("No active tickets. Claim one from the Queue!")

    # --- TAB 3: RESOLVED HISTORY (NEW FEATURE) ---
    with tab_history:
        st.markdown("#### 🗄️ Resolution Archives")
        resolved_tickets = df[df['status'] == 'Resolved']

        if not resolved_tickets.empty:
            col_sel, col_view = st.columns([1, 2])
            
            with col_sel:
                selected_resolved = st.selectbox(
                    "Select Resolved Ticket:",
                    resolved_tickets['ticket_id'].unique(),
                    format_func=lambda x: f"{x} - {resolved_tickets[resolved_tickets['ticket_id']==x]['summary'].values[0]}"
                )
            
            with col_view:
                if selected_resolved:
                    row = resolved_tickets[resolved_tickets['ticket_id'] == selected_resolved].iloc[0]
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="color: #2ea043; margin:0;">✔ {row['ticket_id']}</h3>
                            <span style="background:#2ea043; color:black; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.8em;">RESOLVED</span>
                        </div>
                        <p style="color:#8b949e; font-size:0.9em; margin-top:5px;">📅 {row['timestamp']}</p>
                        
                        <hr style="border-color: #30363d;">
                        
                        <p style="color: #58a6ff; font-weight:bold; margin-bottom:0;">ISSUE SUMMARY</p>
                        <p style="margin-top:0;">{row['summary']}</p>
                        
                        <p style="color: #58a6ff; font-weight:bold; margin-bottom:0;">DEPARTMENT</p>
                        <p style="margin-top:0;">{row['department']}</p>
                        
                        <p style="color: #58a6ff; font-weight:bold; margin-bottom:0;">AI DIAGNOSIS (RCA)</p>
                        <p style="margin-top:0;">{row['rca_hypothesis']}</p>
                        
                        <div style="background-color: #0d1117; padding: 10px; border-left: 3px solid #2ea043; border-radius: 4px; margin-top:10px;">
                            <p style="color: #8b949e; font-size: 0.8em; margin:0;">RESOLUTION / RESPONSE SENT:</p>
                            <p style="margin:5px 0 0 0; font-style:italic;">"{row['response']}"</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No tickets have been resolved yet.")

    # --- TAB 4: DATABASE ---
    with tab_db:
        st.dataframe(df, use_container_width=True)
