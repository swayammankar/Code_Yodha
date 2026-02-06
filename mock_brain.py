import time
import random
import json

class MockResponse:
    def __init__(self, text):
        self.text = text

class MockModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_content(self, prompt):
        # Fake "Thinking" time
        time.sleep(1.0)
        
        prompt_lower = prompt.lower()
        
        # --- BASE TEMPLATE ---
        base_data = {
            "is_duplicate": False,
            "rca_hypothesis": "Simulated Local Analysis",
            "slack_draft": "Automated alert from Local Backup Brain.",
            "status": "Open",
            "user_contact": "local_user@nexus.corp"
        }

        # --- LOGIC ---
        
        # 1. CRITICAL: Fire, Smoke, Water, Smell
        if any(x in prompt_lower for x in ["fire", "smoke", "smell", "burn", "water", "leak", "spark"]):
            specific_data = {
                "summary": "Hardware Fire Hazard", 
                "urgency": "Critical", 
                "department": "Hardware", 
                "response": "EVACUATE AREA. Fire safety protocols initiated.", 
                "sentiment": "Panic",
                "rca_hypothesis": "Thermal Runaway in Server Rack",
                "slack_draft": "🚨 CRITICAL: Safety hazard detected. Evacuation ordered."
            }
            
        # 2. MEDIUM: Whatsapp, Zoom, Wifi, Slow, Internet, Connect, Down, Glitch, Loading
        elif any(x in prompt_lower for x in ["whatsapp", "zoom", "slack", "wifi", "slow", "internet", "connect", "down", "glitch", "loading", "medium", "latency"]):
            specific_data = {
                "summary": "Service Degradation", 
                "urgency": "Medium", 
                "department": "Network", 
                "response": "Performance degradation detected. Clearing cache and resetting connection.", 
                "sentiment": "Frustrated",
                "rca_hypothesis": "Application/Network Congestion",
                "slack_draft": "⚠️ Network warning: App latency reported."
            }
            
        # 3. HIGH: Crash, Blue Screen, Broken, Boot, Won't Start, NOT WORKING, DEAD
        # <--- ADDED "NOT WORKING" HERE
        elif any(x in prompt_lower for x in ["crash", "blue screen", "broken", "won't start", "boot", "fail", "not working", "dead", "stopped"]):
            specific_data = {
                "summary": "Hardware Failure", 
                "urgency": "High", 
                "department": "Hardware", 
                "response": "Critical hardware error. Technician dispatched.", 
                "sentiment": "Angry",
                "rca_hypothesis": "Disk/Motherboard Failure",
                "slack_draft": "❌ Hardware failure reported. Replacement required."
            }
            
        # 4. LOW: Everything else
        else:
            specific_data = {
                "summary": "General Inquiry", 
                "urgency": "Low", 
                "department": "Support", 
                "response": "Ticket created. A technician will review shortly.", 
                "sentiment": "Neutral",
                "rca_hypothesis": "User Information Request",
                "slack_draft": "Info: Low priority ticket created."
            }

        # MERGE
        final_data = {**base_data, **specific_data}
        return MockResponse(json.dumps(final_data))
