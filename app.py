import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import datetime
import os
import uuid 
import time
import mock_brain         
import admin_dashboard    

# ==========================================
# 1. PAGE CONFIGURATION & VISUAL THEME
# ==========================================
st.set_page_config(page_title="NexusAgent", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOGIN UI ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; font-family: 'Segoe UI', sans-serif; }
    
    /* LOGIN BOX */
    .login-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        height: 100%;
    }
    .login-title { color: #ffffff; font-size: 1.5em; font-weight: 600; margin-bottom: 20px; }
    
    /* STATUS TRACKER CARD */
    .status-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .status-header { font-size: 1.2em; color: #58a6ff; font-weight: 600; margin-bottom: 5px; }
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION & SESSION MANAGEMENT
# ==========================================

if "auth_status" not in st.session_state:
    st.session_state.auth_status = None 
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🛡️ NexusAgent Portal")
    st.markdown("Select your login method below.")
    st.markdown("---")
    
    c1, c_mid, c2 = st.columns([1, 0.1, 1])
    
    # --- LEFT SIDE: USER LOGIN (FIXED TEXT) ---
    with c1:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">User Login</div>
            <p style="color:#8b949e; font-size: 0.9em;">Report issues and track tickets.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔵 Continue with Google", use_container_width=True):
                with st.spinner("Connecting..."):
                    time.sleep(1.0)
                st.session_state.auth_status = "User"
                st.session_state.user_info = {"email": "user@gmail.com", "role": "User"}
                st.rerun()
                
            if st.button("📧 Continue with Email", use_container_width=True):
                st.session_state.auth_status = "User"
                st.session_state.user_info = {"email": "user@email.com", "role": "User"}
                st.rerun()
                
            if st.button("📱 Continue with Phone", use_container_width=True):
                st.session_state.auth_status = "User"
                st.session_state.user_info = {"email": "+91 98765 XXXXX", "role": "User"}
                st.rerun()

    # --- MIDDLE: DIVIDER ---
    with c_mid:
        st.markdown("""<div style="border-left: 1px solid #333; height: 350px; margin: auto;"></div>""", unsafe_allow_html=True)

    # --- RIGHT SIDE: OPERATOR LOGIN ---
    with c2:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">Operator Access</div>
            <p style="color:#8b949e; font-size: 0.9em;">System Admin & Command Center.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            password = st.text_input("Enter Access Code", type="password")
            
            if st.button("🚀 Launch Command Center", use_container_width=True, type="primary"):
                if password == "nexus123":
                    with st.spinner("Verifying Credentials..."):
                        time.sleep(1.0)
                    st.session_state.auth_status = "Admin"
                    st.session_state.user_info = {"email": "admin@nexus.corp", "role": "Operator"}
                    st.rerun()
                else:
                    st.error("Invalid Access Code")

if st.session_state.auth_status is None:
    login_page()
    st.stop()

# ==========================================
# 3. CORE LOGIC
# ==========================================

CSV_FILE = 'ticket_db.csv'

def save_ticket_to_csv(ticket_data):
    columns = [
        "ticket_id", "timestamp", "channel", "user_contact", "status", "urgency", 
        "department", "summary", "raw_issue", "response", "sentiment", 
        "is_duplicate", "rca_hypothesis", "slack_draft"
    ]
    df_new = pd.DataFrame([ticket_data])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, columns=columns)
    else:
        df_new.to_csv(CSV_FILE, mode='a', header=False, index=False, columns=columns)

def get_active_incidents_context():
    context_str = "None. System is healthy."
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            if not df.empty and 'status' in df.columns and 'urgency' in df.columns:
                active_df = df[(df['status'] == 'Open') & (df['urgency'].isin(['High', 'Critical']))]
                if not active_df.empty:
                    issues = []
                    for idx, row in active_df.iterrows():
                        issues.append(f"- Incident: {row['summary']} (Dept: {row['department']})")
                    context_str = "\n".join(issues)
        except Exception: pass 
    return context_str

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 4. CONDITIONAL UI BASED ON ROLE
# ==========================================

with st.sidebar:
    st.title("NexusAgent")
    role_color = "green" if st.session_state.auth_status == "Admin" else "blue"
    st.caption(f"Logged in as: :{role_color}[{st.session_state.user_info['role']}]")
    st.write(f"👤 {st.session_state.user_info['email']}")
    
    st.divider()
    
    # ADMIN ONLY CONTROLS
    api_key = None
    input_channel = "Web Portal" 
    
    if st.session_state.auth_status == "Admin":
        st.subheader("🛠️ Admin Controls")
        input_channel = st.selectbox("Simulate Channel", ["Web Portal", "Email", "WhatsApp", "Slack"])
        api_key = st.text_input("Gemini API Key", type="password")
        
        if st.button("🗑️ Reset DB"):
            if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("Connected to Helpdesk")
        
    st.divider()
    if st.button("🔒 Logout"):
        st.session_state.auth_status = None
        st.session_state.chat_history = []
        st.rerun()

# --- MAIN AREA ROUTING ---

if st.session_state.auth_status == "User":
    # ==========================
    # USER VIEW: CHAT + TRACKER
    # ==========================
    st.title("👋 User Support Portal")
    
    # User Tabs
    u_tab1, u_tab2 = st.tabs(["💬 Report Issue", "🔍 Track Status"])
    
    with u_tab1:
        st.markdown("### Chat with NexusAgent")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ex: My laptop screen is flickering...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            # Logic trigger happens at bottom of file

    with u_tab2:
        st.markdown("### 🎫 Ticket Status Tracker")
        search_id = st.text_input("Enter Ticket ID (e.g. TKT-A1B2C3)")
        
        if st.button("Track Ticket"):
            if os.path.exists(CSV_FILE):
                try:
                    df = pd.read_csv(CSV_FILE)
                    # Filter for the ID (case insensitive search)
                    ticket = df[df['ticket_id'].str.contains(search_id.upper().strip(), na=False)]
                    
                    if not ticket.empty:
                        # Get the first match
                        row = ticket.iloc[0]
                        dept = row['department']
                        status = row['status']
                        urgency = row['urgency']
                        
                        # DYNAMIC STATUS CARD
                        st.markdown(f"""
                        <div class="status-card">
                            <div class="status-header">✅ Ticket Found: {row['ticket_id']}</div>
                            <hr style="border-color: #30363d;">
                            <p><strong>Current Status:</strong> <span style="color: #00ff00;">{status}</span></p>
                            <p><strong>Assigned To:</strong> {dept} Team</p>
                            <p><strong>Priority Level:</strong> {urgency}</p>
                            <br>
                            <p style="background-color: #21262d; padding: 10px; border-radius: 5px;">
                                🚀 <strong>Update:</strong> This ticket has been successfully handed over to the 
                                <strong>{dept}</strong> engineering team. A specialist is reviewing the diagnostics 
                                and will resolve it soon.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Ticket ID not found. Please check and try again.")
                except Exception as e:
                    st.error(f"Error reading database: {e}")
            else:
                st.warning("No tickets in the database yet.")

elif st.session_state.auth_status == "Admin":
    # ==========================
    # ADMIN VIEW: FULL DASHBOARD
    # ==========================
    tab1, tab2 = st.tabs(["💬 Triage Console", "📊 Command Center"])
    
    with tab1:
        st.subheader(f"Incoming Feed: {input_channel}")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        user_input = st.chat_input("Simulate incoming ticket...")
        
    with tab2:
        admin_dashboard.render_admin_dashboard()


# ==========================================
# 5. SHARED AI PROCESSING LOGIC
# ==========================================

if 'user_input' in locals() and user_input:
    
    text_response = ""
    try:
        if api_key: 
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash-lite-001")
                active_incidents = get_active_incidents_context()
                
                system_prompt = f"""
                You are NexusAgent. Context: {input_channel}.
                Input: "{user_input}"
                Active Incidents: {active_incidents}
                
                RULES:
                - CRITICAL: Fire, Smoke, Security.
                - HIGH: Hardware Crash, Broken.
                - MEDIUM: Software, WiFi, Apps.
                - LOW: Info, Password.
                
                OUTPUT JSON:
                {{
                    "is_duplicate": boolean,
                    "department": "Hardware"|"Network"|"Support",
                    "urgency": "Critical"|"High"|"Medium"|"Low",
                    "summary": "Title",
                    "rca_hypothesis": "Guess",
                    "response": "Polite reply",
                    "slack_draft": "Ops alert"
                }}
                """
                with st.spinner("Analyzing..."):
                    response = model.generate_content(system_prompt)
                    text_response = response.text
            except: raise Exception("API Error")
        else:
             raise Exception("No Key")

    except Exception:
        # Fallback
        local_model = mock_brain.MockModel("local")
        response = local_model.generate_content(user_input)
        text_response = response.text
        if st.session_state.auth_status == "Admin":
            st.toast("Using Local Brain", icon="🧠")

    try:
        clean_text = text_response.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_text)
        
        data["ticket_id"] = f"TKT-{str(uuid.uuid4())[:6].upper()}"
        data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["channel"] = input_channel
        data["user_contact"] = st.session_state.user_info.get('email', 'guest@nexus.corp')
        data["raw_issue"] = user_input
        data["status"] = "Open"
        
        save_ticket_to_csv(data)
        
        st.session_state.chat_history.append({"role": "assistant", "content": data['response']})
        
        # Admin View
        if st.session_state.auth_status == "Admin":
            with tab1:
                 with st.chat_message("assistant"):
                    st.write(data['response'])
                    with st.status("Analysis", expanded=True):
                        st.write(f"**ID:** {data['ticket_id']}")
                        st.write(f"**Urgency:** {data['urgency']}")
                        st.code(data['slack_draft'])
        else:
            # User View (Write to the Report Issue Tab)
             with u_tab1: 
                 with st.chat_message("assistant"):
                    st.write(data['response'])
                    st.success(f"Ticket **{data['ticket_id']}** created. You can track it in the 'Track Status' tab.")
                
    except Exception as e:
        st.error(f"Error: {e}")
