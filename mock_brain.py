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
        time.sleep(1.5)
        
        # 1. Analyze the prompt to make it feel "Smart"
        prompt_lower = prompt.lower()
        
        if "fire" in prompt_lower or "smoke" in prompt_lower:
            data = {"summary": "Hardware Fire Hazard", "urgency": "Critical", "department": "Hardware", "response": "EVACUATE AREA. Fire safety protocols initiated.", "sentiment": "Panic"}
        elif "wifi" in prompt_lower or "net" in prompt_lower or "slow" in prompt_lower:
            data = {"summary": "Network Latency Issue", "urgency": "Medium", "department": "Network", "response": "Detected high packet loss. Resetting AP-404.", "sentiment": "Frustrated"}
        elif "password" in prompt_lower or "login" in prompt_lower:
            data = {"summary": "Access Denied", "urgency": "Low", "department": "Access", "response": "Password reset link sent to registered email.", "sentiment": "Neutral"}
        elif "blue screen" in prompt_lower or "crash" in prompt_lower:
            data = {"summary": "System Crash (BSOD)", "urgency": "High", "department": "Software", "response": "Critical kernel error. Re-imaging required.", "sentiment": "Angry"}
        else:
            # Fallback for unknown issues
            data = {"summary": "General IT Inquiry", "urgency": "Low", "department": "Support", "response": "Ticket created. A technician will review shortly.", "sentiment": "Calm"}

        # Return it formatted exactly like Gemini API
        return MockResponse(json.dumps(data))
