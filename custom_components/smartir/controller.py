from abc import ABC, abstractmethod
from base64 import b64encode
import binascii
import requests
import logging
import json

from homeassistant.const import ATTR_ENTITY_ID
from . import Helper
_LOGGER = logging.getLogger(__name__)

MQTT_CONTROLLER = 'MQTT'
UFOR11_CONTROLLER = 'UFOR11'

ENC_BASE64 = 'Base64'
ENC_HEX = 'Hex'
ENC_PRONTO = 'Pronto'
ENC_RAW = 'Raw'

MQTT_COMMANDS_ENCODING = [ENC_RAW]
LOOKIN_COMMANDS_ENCODING = [ENC_PRONTO, ENC_RAW]
ESPHOME_COMMANDS_ENCODING = [ENC_RAW]
UFOR11_COMMANDS_ENCODING = [ENC_RAW]


def get_controller(hass, controller, encoding, controller_data, delay):
    """Return a controller compatible with the specification provided."""
    controllers = {
        MQTT_CONTROLLER: MQTTController,
        UFOR11_CONTROLLER: UFOR11Controller
    }
    # controller = UFOR11Controller
    try:
        return UFOR11Controller(hass, controller, encoding, controller_data, delay) # controllers[controller](hass, controller, encoding, controller_data, delay)
    except KeyError:
        raise Exception("The controller is not supported.")


class AbstractController(ABC):
    """Representation of a controller."""
    def __init__(self, hass, controller, encoding, controller_data, delay):
        self.check_encoding(encoding)
        self.hass = hass
        self._controller = controller
        self._encoding = encoding
        self._controller_data = controller_data
        self._delay = delay

    @abstractmethod
    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        pass

    @abstractmethod
    async def send(self, command):
        """Send a command."""
        pass

class MQTTController(AbstractController):
    """Controls a MQTT device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in MQTT_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported "
                            "by the mqtt controller.")

    async def send(self, command):
        """Send a command."""
        service_data = {
            'topic': self._controller_data,
            'payload': command
        }

        await self.hass.services.async_call(
            'mqtt', 'publish', service_data)

class UFOR11Controller(MQTTController):
    """Controls a UFO-R11 device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in UFOR11_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported "
                            "by the UFO-R11 controller.")

    async def send(self, command):
        """Send a command."""
        service_data = {
            'topic': self._controller_data,
            'payload': json.dumps({"ir_code_to_send": command})
        }

        await self.hass.services.async_call(
            'mqtt', 'publish', service_data)
