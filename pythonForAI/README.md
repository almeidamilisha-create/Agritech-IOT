# 🌱 Smart Agriculture Groq AI Advisor (`pythonForAI`)

This directory contains the Python AI agent and advisory tools that connect your **Smart Agriculture IoT System** (`Program.ino`) on the ESP8266 to the **Groq API LLM** (`LLaMA-3.1-8B-Instant` / `LLaMA-3.3-70B-Versatile`) for autonomous irrigation decision-making, real-time agronomic analysis, and crop stress monitoring.

---

## 📂 File Overview

| File | Description |
| :--- | :--- |
| **`smart_ag_agent.py`** | **Primary Autonomous AI Agent**. Continuously monitors Blynk telemetry (`V0`-`V8`), uses deterministic Groq JSON reasoning to toggle the pump (`V3`), enforces the **25% low-water safety rule**, and logs status (`V9`) and AI reasoning (`V10`) to the cloud dashboard. |
| **`blynk_client.py`** | Client for the Blynk IoT Cloud REST API. Reads virtual pins (`V0`-`V8`) and supports an offline simulation/demo mode when testing without live hardware. |
| **`agri_ai_advisor.py`** | AI Agronomist engine powered by Groq (`groq` SDK). Generates structured JSON or markdown crop assessments and answers custom farmer questions. |
| **`main.py`** | Command-line interface with single snapshot mode (`--mode once`), automatic continuous monitoring mode (`--mode auto`), and interactive conversational Q&A mode (`--mode interactive`). |
| **`requirements.txt`** | Required Python dependencies (`groq`, `requests`, `python-dotenv`). |
| **`.env.example`** | Template for configuring your `GROQ_API_KEY`, `BLYNK_AUTH_TOKEN`, and `PYTHONDONTWRITEBYTECODE=1` (preventing `__pycache__` clutter). |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and set your API keys:
```bash
cp .env.example .env
```
Inside `.env`, insert your credentials:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
BLYNK_AUTH_TOKEN=your_blynk_auth_token_here
PYTHONDONTWRITEBYTECODE=1
```
*(Note: Both `.env` and `__pycache__/` are ignored by Git in the project root `.gitignore` file.)*

---

## 💻 Running the AI Agent & CLI Tools

### 1. Run the Autonomous AI Irrigation Agent (`smart_ag_agent.py`)
Start the continuous decision loop that polls Blynk every 15 seconds, decides pump actions via Groq LLaMA, and updates your dashboard:
```bash
python3 smart_ag_agent.py
```

### 2. Single Snapshot Assessment (`main.py --mode once`)
Fetches current sensor readings once and outputs an expert AI crop health analysis:
```bash
python3 main.py --mode once
```
To receive structured JSON-style recommendations:
```bash
python3 main.py --mode once --structured
```

### 3. Interactive AI Agronomist Mode (`main.py --mode interactive`)
Start a conversational Q&A loop where you can ask custom agronomy questions while the LLM is fed your live field telemetry:
```bash
python3 main.py --mode interactive
```

---

## 🔗 How It Maps to ESP8266 Virtual Pins

| Virtual Pin | Parameter | Data Type | Notes |
| :---: | :--- | :--- | :--- |
| **`V0`** | Soil Moisture (%) | Integer | 0 - 100% |
| **`V1`** | Temperature (°C) | Float | Ambient DHT11 Temperature |
| **`V2`** | Humidity (%) | Float | Ambient DHT11 Humidity |
| **`V3`** | Pump Switch | Integer | `0` = OFF, `1` = ON (Controlled physically & by `smart_ag_agent.py`) |
| **`V4`** | Manual Slider | Integer | Manual threshold slider |
| **`V5`** | Crop Selection | Integer | `0`=Wheat, `1`=Moong, `2`=Brown Cowpea, `3`=White Cowpea, `4`=Custom |
| **`V6`** | Target Threshold | Integer | Current target moisture threshold (%) |
| **`V7`** | Crop Name | String | Name of active crop |
| **`V8`** | Tank Water Level | Integer | Ultrasonic tank level (%) |
| **`V9`** | AI Status Message | String | **Dashboard status output** from `smart_ag_agent.py` |
| **`V10`** | AI Reasoning Log | String | **AI decision justification log** from `smart_ag_agent.py` |
