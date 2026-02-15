# IOT Integrated Vertical Farm

## Team
- Ahmad Hajjar — 260280
- Hussein Charara — 261831

## Overview
A web-based system that controls a water pump through an Arduino Uno using a Flask REST API and serial communication. The application allows remote start/stop control, automatic cycle timing, and real-time status monitoring.

## Features
- Remote pump control via web interface
- Automatic 15-minute safety shutdown
- Real-time pump status tracking
- Serial communication between Flask and Arduino
- Expandable for sensors (pH, water level, etc.)

## System Architecture
Frontend: Web dashboard (HTML/CSS/JS)  
Backend: Python Flask API  
Communication: USB Serial (PySerial)  
Hardware: Arduino Uno + Relay + Water Pump  

## Hardware Requirements
- Arduino Uno
- Relay module compatible with Arduino
- Water pump with external power supply
- USB cable for Arduino connection

## Software Requirements
- Python 3.x
- Flask
- PySerial
- Arduino IDE

Install dependencies:

```bash
pip install flask pyserial
```

## Running the System

### 1. Upload Arduino Firmware
Upload the Arduino sketch that listens for:
```
START
STOP
STATUS
```

### 2. Start Flask Server
```bash
python app.py
```

Server runs at:
```
http://localhost:5000
```

### 3. Use the Web Interface
- Press START → Pump turns ON
- Press STOP → Pump turns OFF
- Status updates automatically

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| POST | /api/pump/start | Start pump |
| POST | /api/pump/stop | Stop pump |
| GET | /api/pump/status | Get pump state |
| GET | /api/ph/data | Sample pH data |

## Notes
- Close Arduino Serial Monitor before running Flask.
- Ensure correct COM port is selected or auto-detected.
- Relay logic may be active-LOW depending on module.

## Future Improvements
- WiFi-enabled controller (ESP32)
- Database logging
- Mobile-friendly UI
- Sensor integration and alerts
