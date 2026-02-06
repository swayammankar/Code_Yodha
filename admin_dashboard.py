import streamlit as st
import pandas as pd
import os

# This file is a MODULE. It only contains the Admin Logic.
# Your team will import this file.

def render_admin_dashboard():
    # --- 1. ROBUST FILE LOADING ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'ticket_db.csv')
    
    # Initialize empty dataframe to prevent crashes
    df = pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.warning("⚠️ Database not found! Waiting for tickets...")
        return

    # --- 2. SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Admin Filters")
    all_status = ["All"]
    if not df.empty and 'status' in df.columns:
        all_status += list(df['status'].unique())
    
    # Unique key ensures this widget doesn't clash with others
    selected_status = st.sidebar.selectbox("Filter by Status", all_status, key="admin_status_filter")

    # --- 3. FILTER LOGIC ---
    if selected_status != "All":
        filtered_df = df[df['status'] == selected_status]
    else:
        filtered_df = df

    # --- 4. DISPLAY DASHBOARD ---
    col_header, col_btn = st.columns([4,1]) 
    with col_header:
        st.header("🎛️ Live Ticket Monitor")
    with col_btn:
        if st.button("🔄 Refresh", type="primary", key="refresh_btn"):
            st.rerun()

    # Metrics
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Tickets", len(df))
        
        # Check for High urgency
        if 'urgency' in df.columns:
            # We count both 'High' and 'Critical' as High Priority
            high_count = len(df[df['urgency'].isin(['High', 'Critical'])])
            c2.metric("High Priority", high_count)
        else:
            c2.metric("High Priority", 0)
            
        # Check for Open status
        if 'status' in df.columns:
            c3.metric("Open Issues", len(df[df['status'] == 'Open']))
        else:
            c3.metric("Open Issues", 0)

        # Table with Colors
        st.subheader("Ticket Database")
        def highlight_high_urgency(val):
            if val == 'Critical':
                return 'background-color: #8B0000; color: white; font-weight: bold'
            elif val == 'High':
                return 'background-color: #ffcccc; color: red; font-weight: bold'
            return ''

        # Display Dataframe with safer column selection
        if not filtered_df.empty:
            st.dataframe(filtered_df.style.map(highlight_high_urgency, subset=['urgency']), use_container_width=True)

        # --- 5. CHARTS (The Fixed Color Logic) ---
        st.markdown("---")
        st.subheader("Analytics Overview 📊")
        cc1, cc2 = st.columns(2)
        
        with cc1:
            st.write("*By Department*")
            if 'department' in df.columns: 
                st.bar_chart(df['department'].value_counts())
            elif 'category' in df.columns:
                st.bar_chart(df['category'].value_counts())
        
        with cc2:
            st.write("*By Urgency*")
            if 'urgency' in df.columns:
                # This defines specific colors for specific labels
                urgency_colors = {
                    "Low": "#00CC96",     # Green
                    "Medium": "#FFA500",  # Orange
                    "High": "#FF4B4B",    # Red
                    "Critical": "#8B0000" # Dark Red
                }
                
                # Get the counts for each urgency level
                chart_data = df['urgency'].value_counts()
                
                # Map the colors dynamically based on what urgencies exist in the data
                chart_colors = [urgency_colors.get(x, "#888888") for x in chart_data.index]
                
                st.bar_chart(chart_data, color=chart_colors)
