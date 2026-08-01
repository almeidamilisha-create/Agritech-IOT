<div align="center">
  <img src="banner.svg" alt="Smart Agriculture IoT System Banner" />
</div>

<br>

This project is a comprehensive **Smart Agriculture IoT System** built using the ESP8266 microcontroller, the Blynk IoT Cloud platform, and an **Agentic AI Decision Engine (`smart_ag_agent.py`)** powered by the Groq API LLM (`LLaMA-3.1-8B-Instant`). It continuously monitors environmental and soil parameters, provides automated and AI-reasoned water pump control based on crop needs, and ensures complete hardware safety by preventing dry-running.

## 🌟 Features

- **Real-Time Monitoring**: Tracks soil moisture, ambient temperature, humidity, and water tank levels continuously.
- **Crop-Based Smart Irrigation**: Automatically controls the water pump based on specific moisture thresholds required by different crops (Wheat, Moong, Brown Cowpea, White Cowpea, or Custom).
- **🤖 Agentic AI Irrigation Controller (`pythonForAI/smart_ag_agent.py`)**:
  - Uses **Groq API LLaMA-3.1-8B-Instant** with deterministic JSON schema reasoning.
  - Autonomously evaluates live sensor telemetry (soil moisture vs. target threshold, ambient temperature, humidity, and water tank level) to make optimal irrigation decisions.
  - Enforces absolute hardware safety guardrails: if tank water level drops below 25%, the AI shuts off the pump immediately regardless of soil moisture.
  - Outputs real-time **AI Status Messages** (`V9`) and comprehensive **AI Reasoning Logs** (`V10`) directly to your Blynk Dashboard.
- **Interactive AI Agronomy Advisor (`pythonForAI/main.py`)**: A command-line advisor where farmers can ask custom crop questions with real-time field telemetry injected into the LLM context.
- **Hardware Safety**: Uses an HC-SR04 ultrasonic sensor to monitor the water tank level. The pump is automatically disabled if the water level falls below 25%.
- **Local Display**: View real-time statistics, selected crop, target threshold, and pump status on a 128x64 OLED display.
- **Cloud Dashboard**: Full remote monitoring and control using the Blynk IoT platform.

## 🛠️ Hardware Requirements

- **Microcontroller**: ESP8266 (e.g., NodeMCU or Wemos D1 Mini)
- **Sensors**:
  - DHT11 (Temperature & Humidity Sensor)
  - Analog Soil Moisture Sensor
  - HC-SR04 Ultrasonic Sensor (for water tank level)
- **Display**: 0.96" I2C OLED Display (SSD1306, 128x64)
- **Actuator**: 5V Relay Module & Submersible Water Pump
- Jumper wires & Breadboard
- Power supply for ESP8266 and the Water Pump

## 🔌 Pin Connections

| Component | ESP8266 Pin | Notes |
| :--- | :--- | :--- |
| **DHT11 Sensor** | GPIO 2 (D4) | Requires a pull-up resistor (often built into the module) |
| **Soil Moisture** | A0 (Analog) | Reads raw analog values (Dry: ~1024, Wet: ~400) |
| **Relay Module**| GPIO 14 (D5)| Controls the water pump (Active HIGH) |
| **Ultrasonic Trig**| GPIO 12 (D6)| Trigger pin for HC-SR04 |
| **Ultrasonic Echo**| GPIO 13 (D7)| Echo pin for HC-SR04 |
| **OLED SDA** | SDA Pin | Usually GPIO 4 (D2) on NodeMCU |
| **OLED SCL** | SCL Pin | Usually GPIO 5 (D1) on NodeMCU |

## 🧩 Circuit Explanation

The circuit is designed to act as a complete standalone IoT agricultural node:
1. **The Brain (ESP8266)**: Acts as the central controller, gathering data from all sensors via analog and digital pins, and communicating with the Blynk cloud over WiFi.
2. **Moisture Sensing (Analog Input)**: The Soil Moisture Sensor is connected to the `A0` analog pin. It measures the resistance in the soil (more water = lower resistance). The ESP8266 maps this raw 0-1024 value into a 0-100% moisture reading.
3. **Environmental Sensing (Digital Input)**: The DHT11 sensor uses a single digital pin (`D4`) to send multiplexed temperature and humidity data to the ESP8266.
4. **Water Level Sensing (Ultrasonic)**: The HC-SR04 uses two pins (`D6` for Trig, `D7` for Echo). The ESP8266 sends a sound pulse and measures the time it takes to bounce back from the water surface, calculating the exact volume/level of water remaining in the tank.
5. **Actuation (Relay & Pump)**: A 5V Relay module is connected to `D5`. Since the ESP8266's GPIOs cannot provide enough current to drive a water pump directly, the ESP8266 sends a low-current control signal to the Relay. The Relay acts as an electronic switch, completing the high-current circuit for the water pump when triggered.
6. **Local Feedback (OLED)**: The SSD1306 OLED display is connected via the I2C bus (`SDA` and `SCL`), allowing it to receive and draw text displaying all system metrics in real-time.

## 📚 Required Libraries

Make sure to install the following libraries in your Arduino IDE via the Library Manager (`Sketch > Include Library > Manage Libraries...`):

1. `Blynk` by Volodymyr Shymanskyy
2. `Adafruit GFX Library` by Adafruit
3. `Adafruit SSD1306` by Adafruit
4. `DHT sensor library` by Adafruit (also requires `Adafruit Unified Sensor`)

## 📱 Blynk App Configuration

Create a new project in your Blynk IoT Dashboard and configure the Datastreams as follows:

| Virtual Pin | Data Type | Description |
| :---: | :--- | :--- |
| **V0** | Integer | Soil Moisture (%) |
| **V1** | Double/Float | Temperature (°C) |
| **V2** | Double/Float | Humidity (%) |
| **V3** | Integer | Pump Switch (0 = Off, 1 = On) / Manual & AI Override |
| **V4** | Integer | Manual Threshold Slider (0-100) |
| **V5** | Integer | Crop Selection Menu (0=Wheat, 1=Moong, 2=Brown Cowpea, 3=White Cowpea, 4=Custom) |
| **V6** | Integer | Target Crop Threshold (%) |
| **V7** | String | Current Crop Name |
| **V8** | Integer | Water Tank Level (%) |
| **V9** | String | **AI Dashboard Status Message** (Outputs from `smart_ag_agent.py`) |
| **V10** | String | **AI Reasoning Log** (Outputs from `smart_ag_agent.py`) |

## 🚀 Setup & Installation (ESP8266 Firmware)

1. **Clone or Download** this repository.
2. Open `Program.ino` in the Arduino IDE.
3. Update the Blynk credentials at the top of the file with your specific Template ID, Name, and Auth Token:
   ```cpp
   #define BLYNK_TEMPLATE_ID "Your_Template_ID"
   #define BLYNK_TEMPLATE_NAME "Your_Template_Name"
   #define BLYNK_AUTH_TOKEN "Your_Auth_Token"
   ```
4. Update your WiFi credentials:
   ```cpp
   char ssid[] = "Your_WiFi_SSID";
   char pass[] = "Your_WiFi_PASSWORD";
   ```
5. **Calibrate Sensors**:
   - Depending on your soil sensor and tank dimensions, you may need to adjust the calibration values:
     ```cpp
     const int DRY_VALUE = 1024; // Raw analog value when completely dry
     const int WET_VALUE = 400;  // Raw analog value when submerged in water
     const int BOTTLE_EMPTY = 10; // Distance (cm) when tank is empty
     const int BOTTLE_FULL = 2;   // Distance (cm) when tank is full
     ```
6. Select your ESP8266 board and correct COM port in the Arduino IDE.
7. Click **Upload** to flash the code to your ESP8266.

## 🤖 Groq AI Agent Setup (`pythonForAI/`)

The `pythonForAI/` directory contains Python scripts for AI-driven irrigation decisions and interactive agronomy assistance using **Groq API LLM (`LLaMA-3.1-8B-Instant`)**:

- **`smart_ag_agent.py`**: Autonomous AI loop that evaluates live Blynk sensor telemetry every 15 seconds, decides pump actuation (`V3`), and pushes AI status (`V9`) and reasoning logs (`V10`).
- **`main.py`**: Command-line interactive advisor supporting `--mode once`, `--mode auto`, and conversational Q&A (`--mode interactive`).
- **`blynk_client.py`**: Reliable HTTP client for Blynk REST API with automatic offline simulation/demo mode.
- **`agri_ai_advisor.py`**: Specialist agronomy assessment engine powered by Groq.

### 1. Install Python Dependencies
```bash
cd pythonForAI
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and set your Groq API key and Blynk token:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
BLYNK_AUTH_TOKEN=your_blynk_auth_token_here
PYTHONDONTWRITEBYTECODE=1
```
*(Note: `.env` and `__pycache__/` are automatically ignored by Git in `.gitignore` to keep your credentials clean and prevent bytecode clutter.)*

### 3. Run the Autonomous AI Agent
To start the continuous AI decision loop:
```bash
python3 smart_ag_agent.py
```
To run the interactive agronomy advisor:
```bash
python3 main.py --mode interactive
```

## 📷 Project Gallery

Here are some images of the hardware setup and outputs.

<div align="center">
  <img src="OUTPUT/1.jpeg" width="30%" alt="Hardware Setup 1" />
  <img src="OUTPUT/2.jpeg" width="30%" alt="Hardware Setup 2" />
  <img src="OUTPUT/3.jpeg" width="30%" alt="Hardware Setup 3" />
  <br><br>
  <img src="OUTPUT/4.jpeg" width="30%" alt="Hardware Setup 4" />
  <img src="OUTPUT/5.jpeg" width="30%" alt="Hardware Setup 5" />
  <img src="OUTPUT/6.jpeg" width="30%" alt="Hardware Setup 6" />
</div>

## 🧠 How it Works (Logic)

The system operates on a dual-layer hardware & AI control loop:
1. **Hardware Loop (`Program.ino`)**: Runs every 2 seconds on the ESP8266, gathering soil moisture, DHT11 temp/humidity, and ultrasonic tank level readings, then publishing them to Blynk virtual pins (`V0`, `V1`, `V2`, `V6`, `V7`, `V8`).
2. **AI Agent Loop (`smart_ag_agent.py`)**:
   - Polls numeric telemetry from Blynk every 15 seconds.
   - Evaluates rules via **Groq API LLM (`LLaMA-3.1-8B-Instant`)**:
     - Turn pump **ON** (`V3 = 1`) if `Soil Moisture < Target Threshold` **AND** `Water Tank Level >= 25%`.
     - Turn pump **OFF** (`V3 = 0`) if `Soil Moisture >= Target Threshold` **OR** `Water Tank Level < 25%`.
   - Sends real-time **Status Messages** to `V9` and **Reasoning Justifications** to `V10` for full observability in the Blynk dashboard.
3. **Hardware Safety Guard**: Regardless of manual overrides or AI commands, if the physical ultrasonic sensor reads a tank level below 25%, the ESP8266 firmware forcefully disables the relay to prevent motor dry-running.

---

<div align="center">
  <h3>🌱 Cultivating the future with IoT and AI Automation</h3>
  <img src="https://img.shields.io/badge/Project-Smart%20Agriculture-2ea44f?style=for-the-badge&logo=espressif&logoColor=white" alt="Smart Agriculture" />
  <img src="https://img.shields.io/badge/Status-Active-2ea44f?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Platform-Blynk_IoT-2ea44f?style=for-the-badge&logo=arduino&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/AI-Groq%20LLaMA--3.1-f55036?style=for-the-badge&logo=ai&logoColor=white" alt="Groq AI" />
  <p><i>Designed for efficient, remote-controlled, and AI-optimized farming.</i></p>
</div>
