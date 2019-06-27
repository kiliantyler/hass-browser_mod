import logging
import voluptuous as vol

from homeassistant.components.websocket_api import websocket_command, result_message, event_message, async_register_command
from homeassistant.helpers.entity import Entity, async_generate_entity_id

from .const import DOMAIN, DATA_DEVICES, DATA_ADDERS, WS_CONNECT, WS_UPDATE

_LOGGER = logging.getLogger(__name__)


def setup_connection(hass):
    async_register_command(hass, handle_connect)
    async_register_command(hass, handle_update)
    _LOGGER.error(f"Registered connect ws command")


@websocket_command({
    vol.Required("type"): WS_CONNECT,
    vol.Required("deviceID"): str,
})
def handle_connect(hass, connection, msg):
    _LOGGER.error(f"Got connection {msg}")

    devices = hass.data[DOMAIN][DATA_DEVICES]
    deviceID = msg["deviceID"]
    if deviceID in devices:
        devices[deviceID].ws_connect(connection, msg["id"])
    else:
        adder = hass.data[DOMAIN][DATA_ADDERS][0]
        devices[deviceID] = adder(hass, deviceID, connection, msg["id"])
    connection.send_message(result_message(msg["id"]))


@websocket_command({
    vol.Required("type"): WS_UPDATE,
    vol.Required("deviceID"): str,
    vol.Optional("data"): dict,
})
def handle_update(hass, connection, msg):
    devices = hass.data[DOMAIN][DATA_DEVICES]
    deviceID = msg["deviceID"]
    if deviceID in devices:
        devices[deviceID].ws_update(msg.get("data", None))


class BrowserModEntity(Entity):
    def __init__(self, hass, deviceID, alias=None):
        self.hass = hass
        self.deviceID = deviceID
        self.alias = alias
        self.ws_data = {}
        self.entity_id = async_generate_entity_id("media_player.{}", alias or deviceID, hass=hass)

    def ws_send(self, command, data=None):
        data = data or {}
        self.ws_connection.send_message(event_message(self.ws_cid, {
            "command": command,
            **data,
            }))

    def ws_connect(self, connection, cid):
        self.ws_cid = cid
        self.ws_connection = connection
        _LOGGER.error(f"Connecting {self.entity_id}")
        self.ws_send("update")

    def ws_update(self, data):
        self.ws_data = data
        self.schedule_update_ha_state()
        pass
