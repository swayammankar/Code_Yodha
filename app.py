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


# 1. PAGE CONFIGURATION & VISUAL THEME

st.set_page_config(page_title="NexusAgent", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR "NEON NEBULA" BACKGROUND ---
st.markdown("""
<style>
    /* IMPORT TECH FONT */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

    /* ANIMATED VIBRANT BACKGROUND */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #020024, #090979, #2c003e, #00d4ff);
        background-size: 400% 400%;
        animation: gradient-animation 15s ease infinite;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* GLOWING GRID OVERLAY */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 242, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 242, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        pointer-events: none;
        z-index: 1;
    }

    /* GLASSMORPHISM CARDS */
    div[data-testid="stStatusWidget"], .stChatMessage, section[data-testid="stSidebar"] {
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* TEXT GLOW */
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #fff !important;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
    }
    
    p, label, div {
        color: #e0e0e0 !important;
        text-shadow: 0 0 2px rgba(0,0,0,0.8);
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6);
        border-right: 1px solid rgba(0, 212, 255, 0.3);
    }

    /* INPUT FIELDS - NEON BORDERS */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #00d4ff !important;
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
    }
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
        border-color: #00d4ff;
    }

    /* HOVER BUTTONS */
    .stButton > button {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #00d4ff;
        color: #000;
        box-shadow: 0 0 30px #00d4ff;
        transform: scale(1.05);
    }
    
    /* LOGIN CARD */
    .login-card {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid #00d4ff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 0 50px rgba(0, 212, 255, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    /* ANIMATED SCAN LINE ON LOGIN CARD */
    .login-card::after {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent);
        animation: scan 3s infinite;
    }
    
    @keyframes scan {
        0% { left: -100%; }
        100% { left: 100%; }
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION LAYER
# ==========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # VIBRANT LOGIN SCREEN
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="login-card">
                <h1 style="font-size: 3.5em; margin-bottom: 0;">NEXUS<span style="color:#00d4ff">AGENT</span></h1>
                <p style="color:#00d4ff !important; letter-spacing: 6px; font-weight: bold;">SECURE OPS TERMINAL</p>
                <div style="height: 1px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); width: 80%; margin: 20px auto;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        password = st.text_input("ENTER ACCESS CODE", type="password")
        
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            if password == "nexus123":
                with st.spinner("🚀 INITIATING SECURE HANDSHAKE..."):
                    time.sleep(1.5)
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ ACCESS DENIED")
    return False

if not check_password():
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM CONTROLS")
    input_channel = st.selectbox("SOURCE FEED", ["Web Portal", "Email", "WhatsApp", "Slack", "Voice"])
    st.markdown("---")
    user_contact = st.text_input("OPERATOR ID", value="admin@nexus.corp")
    api_key = st.text_input("GEMINI KEY", type="password")
    st.markdown("---")
    if st.button("🗑️ FLUSH DATABASE"):
        if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
        st.session_state.chat_history = []
        st.rerun()
    if st.button("🔒 TERMINATE SESSION"):
        st.session_state.password_correct = False
        st.rerun()
            
    st.markdown(
        """
        <div style="margin-top: 50px; text-align: center; color: #555;">
            STATUS: <span style="color: #00d4ff; text-shadow: 0 0 10px #00d4ff;">ONLINE</span>
        </div>
        """, unsafe_allow_html=True
    )

# --- TABS ---
tab1, tab2 = st.tabs(["💬 TRIAGE CONSOLE", "📊 COMMAND CENTER"])

with tab1:
    st.markdown("### 📡 LIVE TRANSMISSION FEED")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Input ticket parameters...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        text_response = ""
        try:
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash-lite-001")
                    active_incidents = get_active_incidents_context()
                    
                    system_prompt = f"""
                    You are NexusAgent. The user is contacting via **{input_channel}**.
                    
                    ### INPUT DATA:
                    1. COMPLAINT: "{user_input}"
                    2. ACTIVE INCIDENTS: {active_incidents}

                    ### URGENCY RULES (STRICT):
                    - CRITICAL: Fire, Smoke, Sparks, Security Breach.
                    - HIGH: Hardware Crash, Blue Screen, Broken Screen, Device Not Working, System Failure, Dead Laptop.
                    - MEDIUM: WiFi, WhatsApp, Slack, Zoom, Slow Apps, Internet Connection.
                    - LOW: Password Reset, Information Request, "How do I", Feature Request.

                    ### OUTPUT JSON:
                    {{
                        "is_duplicate": true/false,
                        "department": "Hardware" | "Network" | "Software" | "Access" | "General",
                        "urgency": "Critical" | "High" | "Medium" | "Low",
                        "summary": "Technical Title",
                        "rca_hypothesis": "Technical Guess",
                        "response": "Reply to user (Context aware)",
                        "slack_draft": "Ops Alert",
                        "sentiment": "Neutral" | "Angry" | "Panic"
                    }}
                    """

                    with st.spinner("🧠 NEURAL NETWORK ANALYZING..."):
                        response = model.generate_content(system_prompt)
                        text_response = response.text
                except: raise Exception("Google API Failed")
            else: raise Exception("No API Key")

        except Exception:
            with st.spinner("⚠️ ROUTING TO BACKUP NODE..."):
                local_model = mock_brain.MockModel("local")
                response = local_model.generate_content(user_input)
                text_response = response.text
                st.toast("OFFLINE MODE ENGAGED", icon="🛡️")

        try:
            clean_text = text_response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            
            data["ticket_id"] = f"TKT-{str(uuid.uuid4())[:6].upper()}"
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["channel"] = input_channel 
            data["user_contact"] = user_contact
            data["raw_issue"] = user_input
            data["status"] = "Open"
            
            save_ticket_to_csv(data)
            
            st.session_state.chat_history.append({"role": "assistant", "content": data['response']})
            with st.chat_message("assistant"):
                st.write(data['response'])
                
                with st.status("🔍 ANALYSIS COMPLETE", expanded=True):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**SOURCE:** `{data['channel']}`") 
                    c1.markdown(f"**ID:** `{data['ticket_id']}`")
                    
                    urgency = data.get('urgency', 'Low')
                    color = "green"
                    if urgency == "Critical": color = "red"
                    elif urgency == "High": color = "orange"
                    elif urgency == "Medium": color = "yellow"
                    
                    c1.markdown(f"**URGENCY:** :{color}[{urgency.upper()}]")
                    
                    if data.get('is_duplicate'): 
                        c2.error("⚠️ DUPLICATE DETECTED")
                    else: 
                        c2.success("✅ NEW INCIDENT")
                    
                    st.divider()
                    st.markdown(f"**🧐 RCA HYPOTHESIS:**")
                    st.info(f"{data.get('rca_hypothesis', 'Analyzing...')}")
                    
                    st.markdown("**📢 OPS DRAFT:**")
                    st.code(f"{data.get('slack_draft', 'No draft needed')}", language="bash")
                
        except Exception as e:
            st.error(f"Error processing ticket: {e}")

with tab2:
    admin_dashboard.render_admin_dashboard()
