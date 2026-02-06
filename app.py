import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import datetime
import os
import mock_brain         # Your Backup Brain
import admin_dashboard    # <--- MEMBER 3'S MODULE

# --- PAGE CONFIG ---
st.set_page_config(page_title="NexusAgent", page_icon="🛡️", layout="wide")

# --- FILE SETUP (THE BRIDGE) ---
CSV_FILE = 'ticket_db.csv'

def save_ticket_to_csv(ticket_data):
    """Saves a single ticket dictionary to the CSV file."""
    df_new = pd.DataFrame([ticket_data])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False)
    else:
        df_new.to_csv(CSV_FILE, mode='a', header=False, index=False)

# --- 1. SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("NexusAgent")
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    
    if st.button("🗑️ Reset Database"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        st.session_state.chat_history = []
        st.rerun()

# --- 3. MAIN TABS ---
tab1, tab2 = st.tabs(["💬 User Simulation", "📊 Nexus Command Center"])

# ==========================================
# TAB 1: USER SIMULATION
# ==========================================
with tab1:
    st.subheader("Simulate Incoming Ticket")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Describe your IT issue...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # --- BRAIN LOGIC ---
        text_response = ""
        try:
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash-lite-001")
                    with st.spinner("Analyzing..."):
                        response = model.generate_content(f"""
                        Act as IT Support. Return raw JSON. Schema: 
                        {{"summary": "title", "urgency": "High/Medium/Low", "department": "Hardware/Network/Software", "response": "reply"}}
                        User Complaint: {user_input}
                        """)
                        text_response = response.text
                except:
                    raise Exception("Google API Failed")
            else:
                raise Exception("No API Key")

        except Exception:
            # FALLBACK TO MOCK
            with st.spinner("⚠️ Switching to Local Brain..."):
                local_model = mock_brain.MockModel("local-backup")
                response = local_model.generate_content(user_input)
                text_response = response.text
                st.toast("Using Local Backup", icon="🛡️")

        # --- SAVE TO CSV (THE FIX) ---
        try:
            clean_text = text_response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            
            # Add Missing Fields for Member 3's Dashboard
            data["time"] = datetime.datetime.now().strftime("%H:%M:%S")
            data["status"] = "Open"  # Member 3 filters by this!
            
            # SAVE TO FILE
            save_ticket_to_csv(data)
            
            ai_reply = f"**Ticket Created!** ✅\n\n{data['response']}\n\n*Classified as: {data['department']} ({data['urgency']})*"
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.write(ai_reply)
                
        except Exception as e:
            st.error(f"Error processing ticket: {e}")

# ==========================================
# TAB 2: ADMIN DASHBOARD (MEMBER 3'S CODE)
# ==========================================
with tab2:
    # CALL THE FUNCTION FROM MEMBER 3'S FILE
    admin_dashboard.render_admin_dashboard()
