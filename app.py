import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import datetime
import os
import uuid 
import time
from PIL import Image 
import mock_brain         
import admin_dashboard    

# ==========================================
# 1. PAGE CONFIGURATION & VISUAL THEME
# ==========================================
st.set_page_config(page_title="NexusAgent", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; font-family: 'Segoe UI', sans-serif; }
    
    .login-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        height: 100%;
    }
    .status-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION & SESSION
# ==========================================

if "auth_status" not in st.session_state:
    st.session_state.auth_status = None 
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🛡️ NexusAgent Portal")
    c1, c_mid, c2 = st.columns([1, 0.1, 1])
    
    # --- LEFT: END USER LOGIN ---
    with c1:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">User Login</div>
            <p style="color:#8b949e;">Report issues & track status.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔵 Continue with Google", use_container_width=True):
                with st.spinner("Connecting..."): time.sleep(1.0)
                st.session_state.auth_status = "User"
                st.session_state.user_info = {"email": "user@gmail.com", "role": "User"}
                st.rerun()
            if st.button("📧 Continue with Email", use_container_width=True):
                st.session_state.auth_status = "User"
                st.session_state.user_info = {"email": "user@email.com", "role": "User"}
                st.rerun()

    with c_mid:
        st.markdown("""<div style="border-left: 1px solid #333; height: 350px; margin: auto;"></div>""", unsafe_allow_html=True)

    # --- RIGHT: AGENT/ADMIN LOGIN ---
    with c2:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">Agent Access</div>
            <p style="color:#8b949e;">Support Team Terminal.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            password = st.text_input("Enter Access Code", type="password")
            if st.button("🚀 Launch Terminal", use_container_width=True, type="primary"):
                if password == "nexus123":
                    st.session_state.auth_status = "Admin"
                    st.session_state.user_info = {"email": "agent@nexus.corp", "role": "Operator"}
                    st.rerun()
                else: st.error("Invalid Access Code")

if st.session_state.auth_status is None:
    login_page()
    st.stop()

# ==========================================
# 3. CORE LOGIC
# ==========================================

CSV_FILE = 'ticket_db.csv'

def save_ticket_to_csv(ticket_data):
    columns = ["ticket_id", "timestamp", "channel", "user_contact", "status", "urgency", "department", "summary", "raw_issue", "response", "sentiment", "is_duplicate", "rca_hypothesis", "slack_draft"]
    
    for col in columns:
        if col not in ticket_data:
            ticket_data[col] = "N/A"

    df_new = pd.DataFrame([ticket_data])
    if not os.path.exists(CSV_FILE): df_new.to_csv(CSV_FILE, index=False, columns=columns)
    else: df_new.to_csv(CSV_FILE, mode='a', header=False, index=False, columns=columns)

def get_active_incidents_context():
    context_str = "None. System is healthy."
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            active_df = df[(df['status'] == 'Open') & (df['urgency'].isin(['High', 'Critical']))]
            if not active_df.empty:
                issues = [f"- {row['summary']} ({row['department']})" for idx, row in active_df.iterrows()]
                context_str = "\n".join(issues)
        except: pass 
    return context_str

if "chat_history" not in st.session_state: st.session_state.chat_history = []

# ==========================================
# 4. CONDITIONAL UI ROUTING
# ==========================================

with st.sidebar:
    st.title("NexusAgent")
    role_color = "green" if st.session_state.auth_status == "Admin" else "blue"
    st.caption(f"Logged in as: :{role_color}[{st.session_state.user_info['role']}]")
    st.write(f"👤 {st.session_state.user_info['email']}")
    st.divider()
    
    api_key = None
    input_channel = "Web Portal" 
    
    if st.session_state.auth_status == "Admin":
        st.subheader("🛠️ Simulation Controls")
        input_channel = st.selectbox("Channel Source", ["Web Portal", "Email", "WhatsApp", "Slack"])
        api_key = st.text_input("Gemini API Key", type="password")
        if st.button("🗑️ Reset Database"):
            if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
            st.session_state.chat_history = []
            st.rerun()
    else: st.info("Connected to Helpdesk")
        
    st.divider()
    if st.button("🔒 Logout"):
        st.session_state.auth_status = None
        st.session_state.chat_history = []
        st.rerun()

# --- VARIABLES FOR DEMO ---
uploaded_img = None 
voice_simulation = False

# --- USER VIEW ---
if st.session_state.auth_status == "User":
    st.title("👋 User Support Portal")
    u_tab1, u_tab2 = st.tabs(["💬 Report Issue", "🔍 Track Status"])
    
    with u_tab1:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): 
                st.write(msg["content"])
                if "details" in msg:
                    with st.status("Ticket Intelligence Log", expanded=False):
                        st.write(f"**ID:** `{msg['details']['ticket_id']}`")
                        st.write(f"**Urgency:** {msg['details']['urgency']}")
                        st.write(f"**Department:** {msg['details']['department']}")
                        st.info(f"**Hypothesis:** {msg['details']['rca']}")

        # DEMO CONTROLS (Voice & Image)
        c_voice, c_upload, c_space = st.columns([1,1,3])
        with c_voice:
            if st.button("🎤 Voice Note"):
                with st.spinner("Listening..."):
                    time.sleep(1.5)
                    voice_simulation = True
                st.toast("Transcribed!", icon="✅")
        with c_upload:
            uploaded_file = st.file_uploader("📎 Attach", type=['png','jpg'], label_visibility="collapsed")
            if uploaded_file:
                uploaded_img = Image.open(uploaded_file)
                st.image(uploaded_img, width=150)

        # INPUT HANDLING
        default_val = "My server room is overheating!" if voice_simulation else ""
        
        if voice_simulation:
             st.session_state.chat_history.append({"role": "user", "content": f"🎤 [Voice]: {default_val}"})
             user_input = default_val 
        else:
            user_input = st.chat_input("Describe your issue...")
            if user_input: st.session_state.chat_history.append({"role": "user", "content": user_input})

    with u_tab2:
        search_id = st.text_input("Enter Ticket ID (e.g., TKT-123)")
        if st.button("Track"):
            if os.path.exists(CSV_FILE):
                try:
                    df = pd.read_csv(CSV_FILE)
                    ticket = df[df['ticket_id'].str.contains(search_id.upper().strip(), na=False)]
                    if not ticket.empty:
                        row = ticket.iloc[0]
                        s_color = "#00ff00" if row['status'] == 'Resolved' else "#58a6ff" if row['status'] == 'In Progress' else "#ffffff"
                        
                        st.markdown(f"""
                        <div class="status-card">
                            <h3>Ticket: {row['ticket_id']}</h3>
                            <p><strong>Status:</strong> <span style="color: {s_color}; font-weight: bold;">{row['status']}</span></p>
                            <p><strong>Department:</strong> {row['department']}</p>
                            <p><strong>Summary:</strong> {row['summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else: st.error("Ticket not found.")
                except: st.error("Database Error")

# --- ADMIN VIEW ---
elif st.session_state.auth_status == "Admin":
    tab1, tab2 = st.tabs(["💬 Triage", "🛡️ Agent Terminal"])
    with tab1:
        st.subheader(f"Incoming: {input_channel}")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): 
                st.write(msg["content"])
                if "details" in msg:
                    st.caption(f"Details: {msg['details']['ticket_id']} | {msg['details']['urgency']}")
        
        up_file = st.file_uploader("Simulate Attachment", type=['png','jpg'], key="ad_up")
        if up_file: uploaded_img = Image.open(up_file)
        user_input = st.chat_input("Simulate ticket...")
        
    with tab2:
        admin_dashboard.render_admin_dashboard()

# ==========================================
# 5. SMART LOGIC (API + SIMULATION FALLBACK)
# ==========================================

if 'user_input' in locals() and user_input:
    
    text_response = ""
    used_simulation = False

    try:
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-lite-001")
            
            prompt = f"""
            Act as IT Agent. Input: "{user_input}".
            If image attached, analyze it.
            Output JSON: {{
                "is_duplicate": false,
                "department": "Hardware"|"Software",
                "urgency": "High"|"Low",
                "summary": "Title",
                "rca_hypothesis": "Analysis",
                "response": "User reply",
                "slack_draft": "Ops alert",
                "sentiment": "Neutral"|"Panic",
                "status": "Open"
            }}
            """
            
            with st.spinner("AI Analyzing..."):
                if uploaded_img: response = model.generate_content([prompt, uploaded_img])
                else: response = model.generate_content(prompt)
                text_response = response.text

        else: raise Exception("No Key")
    
    except Exception as e:
        used_simulation = True
        user_input_lower = user_input.lower()
        
        # LOGIC: Image Detected
        if uploaded_img:
            simulated_json = {
                "is_duplicate": False, "department": "Hardware", "urgency": "High",
                "summary": "Visual Error Detected (OCR)",
                "rca_hypothesis": "Image analysis detected 'Critical_Process_Died' error code.",
                "response": "I have analyzed your screenshot. It appears to be a Critical System Failure (Blue Screen). I have alerted the Hardware Team immediately.",
                "slack_draft": "🚨 IMAGE ALERT: BSOD detected.", "sentiment": "Panic", "status": "Open"
            }
        
        # LOGIC: Critical Fire/Smoke
        elif "fire" in user_input_lower or "smoke" in user_input_lower:
            simulated_json = {
                "department": "Hardware", "urgency": "Critical", 
                "summary": "Fire Hazard", "rca_hypothesis": "Potential Thermal Runaway",
                "response": "CRITICAL: Evacuate immediately. Fire safety team dispatched.",
                "slack_draft": "🚨 FIRE DETECTED.", "sentiment": "Panic", "status": "Open", "is_duplicate": False
            }
        
        # LOGIC: High Priority Hardware (Laptop/Screen/Crash)
        elif any(x in user_input_lower for x in ["laptop", "screen", "computer", "not working", "crash", "broken", "won't turn on"]):
            simulated_json = {
                "department": "Hardware", "urgency": "High", 
                "summary": "Hardware Malfunction", "rca_hypothesis": "User reported critical device failure.",
                "response": "I have logged a High Priority hardware ticket. A technician will review your device status shortly.",
                "slack_draft": "🚨 HARDWARE FAILURE: User unable to work.", "sentiment": "Frustrated", "status": "Open", "is_duplicate": False
            }
            
        # LOGIC: Spam/Incomplete
        elif len(user_input) < 4:
             simulated_json = { "status": "Ignored", "response": "Please provide a detailed issue.", "sentiment": "Neutral" }
        
        # LOGIC: Low Priority General
        else:
            simulated_json = {
                "department": "Support", "urgency": "Low", 
                "summary": "General Inquiry", "rca_hypothesis": "User reported issue.",
                "response": f"Ticket created. A support agent will check this shortly.",
                "slack_draft": "Info: New ticket logged.", "sentiment": "Neutral", "status": "Open", "is_duplicate": False
            }
        text_response = json.dumps(simulated_json)

    try:
        clean_text = text_response.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_text)
        
        if data.get("status") == "Open":
            data["ticket_id"] = f"TKT-{str(uuid.uuid4())[:6].upper()}"
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["channel"] = input_channel
            data["user_contact"] = st.session_state.user_info.get('email', 'guest')
            data["raw_issue"] = user_input + (" [Image Attached]" if uploaded_img else "")
            
            save_ticket_to_csv(data)
            
            # STORE DETAILS FOR UI
            msg_details = {
                "ticket_id": data["ticket_id"],
                "urgency": data["urgency"],
                "department": data["department"],
                "rca": data["rca_hypothesis"]
            }
            
            st.session_state.chat_history.append({"role": "assistant", "content": data['response'], "details": msg_details})
            
            # Show Response immediately
            msg_area = tab1 if st.session_state.auth_status == "Admin" else u_tab1
            with msg_area:
                with st.chat_message("assistant"):
                    st.write(data['response'])
                    # RESTORED DETAILED VIEW HERE
                    with st.status("Ticket Intelligence Log", expanded=True):
                        st.write(f"**Ticket ID:** `{data['ticket_id']}`")
                        
                        # Colored Urgency
                        if data['urgency'] == 'Critical': st.error(f"**Urgency:** {data['urgency']}")
                        elif data['urgency'] == 'High': st.warning(f"**Urgency:** {data['urgency']}")
                        else: st.info(f"**Urgency:** {data['urgency']}")
                        
                        st.write(f"**Department:** {data['department']}")
                        st.write(f"**RCA Hypothesis:** {data['rca_hypothesis']}")
                        st.code(f"Ops Alert: {data['slack_draft']}", language="text")

        else:
             st.session_state.chat_history.append({"role": "assistant", "content": data['response']})
             msg_area = tab1 if st.session_state.auth_status == "Admin" else u_tab1
             with msg_area:
                 with st.chat_message("assistant"):
                     st.write(data['response'])

    except Exception as e: st.error(f"Error: {e}")
