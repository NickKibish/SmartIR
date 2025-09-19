# Toshiba MQTT Command Tester

This script allows you to test Toshiba AC commands by sending them via MQTT with interactive confirmation for each command.

## Setup

### 1. Activate the Virtual Environment

From the project root directory:

```bash
source venv/bin/activate
```

### 2. Configure MQTT Settings

The script automatically loads configuration from the `.env` file in the project root.

#### Option A: Use .env File (Recommended)

Edit the `.env` file in the project root:

```bash
# MQTT Broker Configuration
MQTT_HOST=localhost
MQTT_PORT=1883

# MQTT Topic (adjust based on your UFO-R11 device name in Zigbee2MQTT)
MQTT_TOPIC=zigbee2mqtt/your_device_name/set

# MQTT Authentication (uncomment and set if needed)
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
```

#### Option B: Use Environment Variables

You can also set environment variables directly (these override .env values):

```bash
export MQTT_HOST="your-mqtt-broker-host"
export MQTT_PORT="1883"
export MQTT_TOPIC="zigbee2mqtt/your_device_name/set"
export MQTT_USERNAME="your-username"  # Optional
export MQTT_PASSWORD="your-password"  # Optional
```

## Usage

### Run the Script

```bash
# Make sure to activate the virtual environment first
source venv/bin/activate

# Run the script (it will automatically load .env configuration)
python scripts/send_toshiba_commands.py
```

### Interactive Operation

The script will:

1. Connect to the MQTT broker
2. Load all commands from `codes/climate/toshiba.json`
3. Display each command and prompt you: "Press Enter to continue or 'q' to quit"
4. Send the command via MQTT when you press Enter
5. Continue to the next command or exit when you press 'q'

### Example Session

```
=== Toshiba MQTT Command Tester ===
Loaded configuration from /path/to/SmartIR/.env
MQTT Host: 192.168.1.100:1883
MQTT Topic: smartir/send_command
Commands file: /path/to/codes/climate/toshiba.json
Successfully connected to MQTT broker
Found 157 total commands

--- Command 1/157: off ---
Command data: CFARUBEzAmwGBeACAwMzAgUCgAMHbAYFAgUCMwLgAQMBBQJADUAX...
Successfully sent command 'off' to topic 'smartir/send_command'
Send next command? (y/n): y

--- Command 2/157: on ---
Command data: B1QRVBEwAnAG4AUDAf0BgANAF8ALwAdAAUAXBXAG/QH9AUAHAzAC...
Successfully sent command 'on' to topic 'smartir/send_command'
Send next command? (y/n): n

User requested to stop. Exiting...
Disconnected from MQTT broker
```

## MQTT Message Format

The script publishes commands in the UFO-R11 compatible format:

```json
{
    "ir_code_to_send": "CFARUBEzAmwGBeACAwMzAgUCgAMHbAYFAgUCMwLgAQMBBQJADUAX..."
}
```

This format is compatible with Zigbee2MQTT UFO-R11 devices. The IR codes from the Toshiba JSON file are sent directly as the `ir_code_to_send` value.

## Command Structure

The Toshiba commands include:

- **Basic controls**: `off`, `on`
- **Heat mode** with fan speeds (`high`, `l4`, `medium`, `l2`, `low`, `auto`, `quiet`) and temperatures (17-30°C)
- **Cool mode** with fan speeds and temperatures
- **Dry mode** with fan speeds and temperatures
- **Heat_cool mode** with fan speeds and temperatures
- **Fan_only mode** with fan speeds

## Error Handling

The script includes comprehensive error handling for:

- MQTT connection failures
- Invalid JSON in command files
- Missing command files
- Network interruptions
- User interruptions (Ctrl+C)

## Troubleshooting

### Connection Issues

1. Verify MQTT broker is running and accessible
2. Check firewall settings
3. Confirm MQTT credentials (if using authentication)
4. Test connection with an MQTT client like `mosquitto_pub`

### Command Issues

1. Ensure `codes/climate/toshiba.json` exists and is valid JSON
2. Check file permissions
3. Verify the command structure matches expected format

### Testing MQTT Connectivity

Test your MQTT setup independently:

```bash
# Subscribe to the topic (in one terminal)
mosquitto_sub -h localhost -t "smartir/send_command"

# Publish a test message (in another terminal)
mosquitto_pub -h localhost -t "smartir/send_command" -m '{"test": "message"}'
```