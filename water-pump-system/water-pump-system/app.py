from flask import Flask, render_template, jsonify, request
import random
from datetime import datetime, timedelta
import time
import threading
import serial
import serial.tools.list_ports

app = Flask(__name__)

# -----------------------------
# Pump state (server-side)
# -----------------------------
pump_state = {
    "is_running": False,
    "start_time": None,
    "cycles_completed": 0,
    "last_device": None,
    "last_arduino_reply": None
}

# -----------------------------
# Serial / Arduino config
# -----------------------------
BAUD = 9600
SERIAL_TIMEOUT = 2  # seconds
AUTO_DETECT = True
SERIAL_PORT = "COM3"

# Cycle duration in seconds (15 minutes)
CYCLE_DURATION = 900

# -----------------------------
# RELAY LOGIC FIX
# -----------------------------
# Most cheap relay modules are ACTIVE LOW:
#   Arduino pin HIGH -> relay OFF -> pump OFF
#   Arduino pin LOW  -> relay ON  -> pump ON
# Set True if your pump runs when Arduino says "OFF"
INVERT_RELAY = True

ser = None
ser_lock = threading.Lock()


def list_ports_debug():
    ports = []
    for p in serial.tools.list_ports.comports():
        ports.append({
            "device": p.device,
            "description": p.description,
            "hwid": p.hwid
        })
    return ports


def guess_arduino_port():
    candidates = []
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        keywords = ["arduino", "ch340", "cp210", "ftdi", "usb serial", "serial"]
        if any(k in desc for k in keywords) or any(k in hwid for k in keywords):
            candidates.append(p.device)
    if candidates:
        return candidates[0]
    all_ports = [p.device for p in serial.tools.list_ports.comports()]
    if len(all_ports) == 1:
        return all_ports[0]
    return None


def connect_serial(force=False):
    global ser
    if ser and ser.is_open and not force:
        return True
    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass

    port = guess_arduino_port() if AUTO_DETECT else SERIAL_PORT
    if not port:
        pump_state["last_device"] = None
        pump_state["last_arduino_reply"] = "ERR NO PORT FOUND"
        return False
    try:
        ser = serial.Serial(port, BAUD, timeout=SERIAL_TIMEOUT)
        time.sleep(2)
        pump_state["last_device"] = port
        pump_state["last_arduino_reply"] = "OK CONNECTED"
        return True
    except Exception as e:
        pump_state["last_device"] = port
        pump_state["last_arduino_reply"] = f"ERR CONNECT {e}"
        return False


def send_cmd(cmd: str) -> str:
    global ser
    if not connect_serial():
        return pump_state.get("last_arduino_reply") or "ERR NO SERIAL"
    with ser_lock:
        try:
            ser.reset_input_buffer()
            ser.write((cmd.strip() + "\n").encode("utf-8"))
            ser.flush()
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                line = "ERR NO RESPONSE"
            pump_state["last_arduino_reply"] = line
            return line
        except Exception as e:
            pump_state["last_arduino_reply"] = f"ERR IO {e}"
            return pump_state["last_arduino_reply"]


def generate_ph_data():
    data = []
    now = datetime.now()
    for i in range(24):
        timestamp = (now - timedelta(hours=23 - i)).strftime("%H:%M")
        ph_value = round(random.uniform(6.5, 7.5), 2)
        data.append({"time": timestamp, "ph": ph_value})
    return data


def get_elapsed():
    """Get elapsed seconds since pump started (server-side tracking)."""
    if pump_state["is_running"] and pump_state["start_time"]:
        return int((datetime.now() - pump_state["start_time"]).total_seconds())
    return 0


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/debug/ports")
def debug_ports():
    return jsonify({
        "ports": list_ports_debug(),
        "selected_port": pump_state.get("last_device"),
        "auto_detect": AUTO_DETECT,
        "invert_relay": INVERT_RELAY
    })


@app.route("/api/pump/start", methods=["POST"])
def start_pump():
    """Start the pump from the user's perspective."""
    if INVERT_RELAY:
        resp = send_cmd("STOP")
        if "OK PUMP OFF" in resp or "ERR ALREADY OFF" in resp:
            pump_state["is_running"] = True
            pump_state["start_time"] = datetime.now()
            return jsonify(success=True, message="PUMP STARTED", state=True)
        return jsonify(success=False, message=resp, state=pump_state["is_running"])
    else:
        resp = send_cmd("START")
        if "OK PUMP ON" in resp:
            pump_state["is_running"] = True
            pump_state["start_time"] = datetime.now()
            return jsonify(success=True, message=resp, state=True)
        elif "ERR ALREADY ON" in resp:
            pump_state["is_running"] = True
            return jsonify(success=True, message=resp, state=True)
        return jsonify(success=False, message=resp, state=pump_state["is_running"])


@app.route("/api/pump/stop", methods=["POST"])
def stop_pump():
    """Stop the pump from the user's perspective."""
    if INVERT_RELAY:
        resp = send_cmd("START")
        if "OK PUMP ON" in resp or "ERR ALREADY ON" in resp:
            if pump_state["is_running"]:
                pump_state["cycles_completed"] += 1
            pump_state["is_running"] = False
            pump_state["start_time"] = None
            return jsonify(success=True, message="PUMP STOPPED", state=False)
        return jsonify(success=False, message=resp, state=pump_state["is_running"])
    else:
        resp = send_cmd("STOP")
        if "OK PUMP OFF" in resp:
            if pump_state["is_running"]:
                pump_state["cycles_completed"] += 1
            pump_state["is_running"] = False
            pump_state["start_time"] = None
            return jsonify(success=True, message=resp, state=False)
        elif "ERR ALREADY OFF" in resp:
            pump_state["is_running"] = False
            pump_state["start_time"] = None
            return jsonify(success=True, message=resp, state=False)
        return jsonify(success=False, message=resp, state=pump_state["is_running"])


@app.route("/api/pump/status")
def pump_status():
    """
    Return pump status using SERVER-SIDE time tracking.
    Does NOT send serial commands — avoids spamming Arduino every second.
    """
    elapsed = get_elapsed()

    # Auto-stop after cycle duration
    if pump_state["is_running"] and elapsed >= CYCLE_DURATION:
        if INVERT_RELAY:
            send_cmd("START")
        else:
            send_cmd("STOP")
        pump_state["cycles_completed"] += 1
        pump_state["is_running"] = False
        pump_state["start_time"] = None
        elapsed = 0

    return jsonify({
        "is_running": pump_state["is_running"],
        "elapsed_time": elapsed,
        "cycle_duration": CYCLE_DURATION,
        "cycles_completed": pump_state["cycles_completed"],
        "serial_port": pump_state.get("last_device"),
        "arduino_reply": pump_state.get("last_arduino_reply")
    })


@app.route("/api/ph/data")
def ph_data():
    return jsonify(generate_ph_data())


if __name__ == "__main__":
    connect_serial()
    app.run(debug=True, host="0.0.0.0", port=5000)