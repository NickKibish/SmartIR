#!/usr/bin/env python3
"""
Standalone MQTT script for testing Toshiba AC commands.

This script loads the Toshiba device codes and sends IR commands via MQTT,
allowing interactive testing of each command with user confirmation.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, List
import paho.mqtt.client as mqtt
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ToshibaMQTTTester:
    """MQTT client for testing Toshiba AC commands."""

    def __init__(self, mqtt_host: str, mqtt_port: int = 1883,
                 mqtt_topic: str = "smartir/send_command",
                 mqtt_username: str = None, mqtt_password: str = None):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.client = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client = mqtt.Client()

            # Set credentials if provided
            if self.mqtt_username and self.mqtt_password:
                self.client.username_pw_set(self.mqtt_username, self.mqtt_password)

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish

            logger.info(f"Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_start()

            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5

            if not self.connected:
                logger.error("Failed to connect to MQTT broker within timeout")
                return False

            return True

        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            self.connected = True
            logger.info("Successfully connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        self.connected = False
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_publish(self, client, userdata, mid):
        """MQTT publish callback."""
        logger.debug(f"Message {mid} published successfully")

    def send_command(self, command_name: str, command_data: str) -> bool:
        """Send IR command via MQTT using UFO-R11 format."""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False

        try:
            # Create MQTT payload for UFO-R11 device
            payload = {
                "ir_code_to_send": command_data
            }

            # Publish command
            result = self.client.publish(self.mqtt_topic, json.dumps(payload))

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Successfully sent command '{command_name}' to topic '{self.mqtt_topic}'")
                return True
            else:
                logger.error(f"Failed to publish command '{command_name}'. Return code: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error sending command '{command_name}': {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


def load_toshiba_commands(json_file_path: str) -> Dict[str, Any]:
    """Load Toshiba device commands from JSON file."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded Toshiba commands from {json_file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"Commands file not found: {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in commands file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading commands file: {e}")
        sys.exit(1)


def extract_all_commands(commands: Dict[str, Any]) -> List[tuple]:
    """Extract all commands from the nested structure."""
    all_commands = []

    def extract_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    # This is a command string
                    all_commands.append((current_path, value))
                else:
                    # Continue recursing
                    extract_recursive(value, current_path)

    extract_recursive(commands)
    return all_commands


def get_user_confirmation() -> bool:
    """Get user confirmation to send next command."""
    response = input("Press Enter to continue or 'q' to quit: ").strip().lower()
    return response != 'q'


def main():
    """Main function."""
    # Load environment variables from .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    env_file = os.path.join(project_root, '.env')

    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded configuration from {env_file}")
    else:
        logger.warning(f"No .env file found at {env_file}, using environment variables")

    # Get configuration from environment variables (from .env or system)
    mqtt_host = os.getenv('MQTT_HOST', 'localhost')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    mqtt_topic = os.getenv('MQTT_TOPIC', 'smartir/send_command')
    mqtt_username = os.getenv('MQTT_USERNAME')
    mqtt_password = os.getenv('MQTT_PASSWORD')

    # Path to Toshiba commands file
    commands_file = os.path.join(project_root, 'codes', 'climate', 'toshiba.json')

    logger.info("=== Toshiba MQTT Command Tester ===")
    logger.info(f"MQTT Host: {mqtt_host}:{mqtt_port}")
    logger.info(f"MQTT Topic: {mqtt_topic}")
    logger.info(f"Commands file: {commands_file}")

    # Load commands
    device_data = load_toshiba_commands(commands_file)
    commands = device_data.get('commands', {})

    if not commands:
        logger.error("No commands found in the device file")
        sys.exit(1)

    # Extract all commands
    all_commands = extract_all_commands(commands)
    logger.info(f"Found {len(all_commands)} total commands")

    # Initialize MQTT client
    mqtt_client = ToshibaMQTTTester(
        mqtt_host=mqtt_host,
        mqtt_port=mqtt_port,
        mqtt_topic=mqtt_topic,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password
    )

    # Connect to MQTT broker
    if not mqtt_client.connect():
        logger.error("Failed to connect to MQTT broker")
        sys.exit(1)

    try:
        # Send commands one by one with user confirmation
        for i, (command_name, command_data) in enumerate(all_commands, 1):
            print(f"\n--- Command {i}/{len(all_commands)}: {command_name} ---")
            print(f"Command data: {command_data[:50]}{'...' if len(command_data) > 50 else ''}")

            # Send command
            success = mqtt_client.send_command(command_name, command_data)

            if not success:
                logger.warning(f"Failed to send command '{command_name}'")

            # Ask for user confirmation before next command (except for last command)
            if i < len(all_commands):
                if not get_user_confirmation():
                    logger.info("User requested to stop. Exiting...")
                    break

        logger.info("Command testing completed")

    except KeyboardInterrupt:
        logger.info("Interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        mqtt_client.disconnect()
        logger.info("Disconnected from MQTT broker")


if __name__ == "__main__":
    main()