# Water Pump Control System - Web Application

A beautiful, professional web application for controlling an Arduino-based water pump system with real-time monitoring and pH level tracking.

## Features

- **Pump Control**: Start/Stop button for 15-minute irrigation cycles
- **Real-time Timer**: Countdown display for current pump cycle
- **Cycle Tracking**: Monitor completed cycles
- **pH Monitoring**: Live chart displaying pH levels over 24 hours
- **Auto-Stop**: Automatic pump shutdown after 15 minutes
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Beautiful UI**: Clean green and white theme with smooth animations

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## How It Works

### Web Application
- **Flask Backend**: Handles API requests and pump state management
- **REST API**: Provides endpoints for pump control and status
- **Real-time Updates**: Status updates every second
- **Chart.js**: Beautiful pH level visualization

### API Endpoints

- `GET /` - Main web interface
- `POST /api/pump/start` - Start the pump (15-minute cycle)
- `POST /api/pump/stop` - Stop the pump manually
- `GET /api/pump/status` - Get current pump status
- `GET /api/ph/data` - Get pH data for chart

## Arduino Integration

To connect your Arduino to this web application, your Arduino needs to:

1. **Connect to WiFi** (use ESP8266 or ESP32)
2. **Poll the API** every second to check pump status
3. **Control the motor** based on the API response

### Arduino Code Structure (Guide)

Your Arduino code should:
```cpp
// Check pump status
GET http://YOUR_SERVER_IP:5000/api/pump/status

// Response will be JSON:
{
    "is_running": true/false,
    "elapsed_time": 0-900,
    "cycles_completed": number
}

// If is_running == true, turn motor ON
// If is_running == false, turn motor OFF
```

### Arduino Pin Connection Example
```
Arduino Pin -> Motor Driver
Pin 7 -> IN1 (Motor Control)
5V -> VCC
GND -> GND

Motor Driver -> Water Pump Motor
OUT1 -> Motor +
OUT2 -> Motor -
```

## Configuration

You can modify these settings in `app.py`:

- **Cycle Duration**: Change `900` (15 minutes) to your desired duration in seconds
- **Port**: Change `port=5000` to use a different port
- **pH Range**: Modify `random.uniform(6.5, 7.5)` for different pH simulation range

## Usage

1. Click "START CYCLE" to begin a 15-minute pump cycle
2. Watch the countdown timer and status indicator
3. The pump will automatically stop after 15 minutes
4. Use "STOP PUMP" to manually stop the cycle if needed
5. Monitor pH levels in the chart on the right

## Notes

- The pH data is randomly generated for demonstration purposes
- Replace with real sensor data by modifying the `generate_ph_data()` function
- The pump state is stored in memory and will reset when the server restarts
- For production use, consider using a database for persistent storage

## Color Scheme

- Primary Green: #4caf50
- Dark Green: #2e7d32
- Light Green: #66bb6a
- White: #ffffff
- Background: #e8f5e9 to #ffffff gradient

## Future Enhancements

- Real pH sensor integration
- Database storage for historical data
- User authentication
- Multiple pump control
- Scheduling capabilities
- Email/SMS notifications
- Water flow monitoring
