#!/usr/bin/env python3
"""
smart_ag_agent.py - Agentic AI decision engine for Smart Agriculture IoT System
using Groq API LLM (LLaMA-3.1-8B-Instant) and Blynk IoT Cloud REST API.
"""

import os
import time
import requests
import json
import urllib.parse  # 🧠 CRITICAL ADDITION: Handles text spacing safely for the cloud API
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# ==========================================
# CONFIGURATION (Supports environment variables with fallback defaults)
# ==========================================
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN", "p5oV-dojaWL9mde_ZxXfd-LJjunCfr3Y")
BLYNK_API_URL = "https://blynk.cloud/external/api"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found! Please set it in pythonForAI/.env or your environment variables.")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# BLYNK API HELPER FUNCTIONS
# ==========================================
def get_blynk_value(pin):
    """Fetches the current value of a specific Virtual Pin from Blynk."""
    url = f"{BLYNK_API_URL}/get?token={BLYNK_AUTH_TOKEN}&{pin}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            val = response.text.strip()
            if not val or val == "None":
                return None
            return val
        return None
    except Exception as e:
        print(f"Error fetching pin {pin}: {e}")
        return None

def set_blynk_value(pin, value):
    """Sends a value/command to a specific Virtual Pin on Blynk using clean URL encoding."""
    safe_value = urllib.parse.quote(str(value))
    url = f"{BLYNK_API_URL}/update?token={BLYNK_AUTH_TOKEN}&{pin}={safe_value}"
    try:
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Error updating pin {pin}: {e}")

# ==========================================
# AI REASONING ENGINE
# ==========================================
def run_agentic_decision():
    print("\n--- Fetching Sensor Data ---")
    
    # Read active datastreams from your Blynk setup
    raw_soil = get_blynk_value("V0")
    raw_temp = get_blynk_value("V1")
    raw_hum = get_blynk_value("V2")
    raw_target = get_blynk_value("V6")
    crop_name = get_blynk_value("V7")
    raw_tank = get_blynk_value("V8")  # 🧠 CRITICAL FIX: Read live tank water level from V8
    
    if not crop_name:
        crop_name = "Wheat"

    # Core guard clause to prevent running if hardware goes offline
    if None in [raw_soil, raw_temp, raw_hum, raw_target]:
        print("Waiting for data from Blynk cloud. Pins might be uninitialized or offline.")
        return

    # 🧠 CRITICAL FIX: Convert API Strings into true Python Numbers for exact math comparisons
    try:
        soil_moisture = int(float(raw_soil))
        temperature = float(raw_temp)
        humidity = int(float(raw_hum))
        target_moisture = int(float(raw_target))
        water_level = int(float(raw_tank)) if raw_tank else 100
    except ValueError:
        print("Error parsing numeric telemetry from string responses.")
        return

    print(f"Crop: {crop_name} | Soil: {soil_moisture}% (Target: {target_moisture}%) | Temp: {temperature}°C | Hum: {humidity}% | Tank: {water_level}%")

    # Construct the System Prompt with strict deterministic guidelines & hardware safety rules
    system_prompt = f"""
    You are an expert Agricultural AI Agent managing an automated IoT irrigation system. 
    Your objective is to evaluate real-time numeric sensor telemetry and determine if the water pump should be turned ON (1) or OFF (0).

    ### 1. ABSOLUTE SYSTEM RULES
    * If Live Soil Moisture ({soil_moisture}) is LESS than Target Moisture Threshold ({target_moisture}) AND Tank Water Level ({water_level}) >= 25%, you MUST set pump_action to 1.
    * If Live Soil Moisture ({soil_moisture}) is EQUAL to or GREATER than Target Moisture Threshold ({target_moisture}), OR if Tank Water Level ({water_level}) < 25%, you MUST set pump_action to 0.
    * If Tank Water Level ({water_level}) is less than 25%, note a LOW WATER TANK CRITICAL WARNING in the reasoning_log.

    ### 2. BLYNK IOT DASHBOARD OUTPUT
    Respond ONLY with a valid JSON object matching this schema. Do not include markdown blocks or extra text.

    {{
      "pump_action": <int>,
      "dashboard_status": "<string>",
      "reasoning_log": "<string>"
    }}
    """

    user_prompt = f"""
    Current Metrics:
    - Target Crop: {crop_name}
    - Live Soil Moisture: {soil_moisture}%
    - Target Moisture Threshold: {target_moisture}%
    - Temperature: {temperature}°C
    - Environmental Humidity: {humidity}%
    - Tank Water Level: {water_level}%
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant", 
            response_format={"type": "json_object"},
            temperature=0.1 
        )

        # Parse JSON
        ai_response = json.loads(chat_completion.choices[0].message.content)
        pump_command = ai_response.get("pump_action", 0)
        status_msg = ai_response.get("dashboard_status", "System Error")
        reasoning = ai_response.get("reasoning_log", "No reasoning provided.")

        print(f"🧠 AI Decision: {'TURN PUMP ON' if pump_command == 1 else 'LEAVE PUMP OFF'}")
        print(f"📊 Status: {status_msg}")
        print(f"🗣️ Reasoning: {reasoning}")

        # Send updates out to the proper Blynk Pins cleanly without overwriting V8 Tank Level
        set_blynk_value("V3", pump_command)    # 🧠 CRITICAL FIX: V3 controls the physical water pump (matching Program.ino)
        set_blynk_value("V9", status_msg)      # 🧠 CRITICAL FIX: Use V9 for dashboard status message
        set_blynk_value("V10", reasoning)      # 🧠 CRITICAL FIX: Use V10 for reasoning log (V8 is reserved for Tank Level)

    except Exception as e:
        print(f"Error during AI reasoning or JSON parsing: {e}")

# ==========================================
# MAIN LOOP
# ==========================================
if __name__ == "__main__":
    print("Starting AI Smart Agriculture Agent...")
    while True:
        run_agentic_decision()
        time.sleep(15)  # 🧠 CRITICAL FIX: Polling every 15s to respect Groq rate limits while staying responsive