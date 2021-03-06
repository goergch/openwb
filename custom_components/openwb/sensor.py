from .const import SENSOR_DEFINITIONS, DEFAULT_BASE_TOPIC, DOMAIN

from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
import logging
from typing import Optional, Dict, Any


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    sensors = []

    for topic in SENSOR_DEFINITIONS:
        sensors.append(OpenWBSensor(topic))

    async_add_entities(sensors)


class OpenWBSensor(Entity):
    def __init__(self, topic):
        self._definition = SENSOR_DEFINITIONS[topic]
        self._unique_id = DOMAIN + "_" + self._definition.get("entity_id")
        self._topic = DEFAULT_BASE_TOPIC + topic
        self._name = self._definition.get("name")
        self._device_class = self._definition.get("device_class")
        self._enable_default = self._definition.get("enable_default")
        self._unit_of_measurement = self._definition.get("unit")
        self._icon = self._definition.get("icon")
        self._transform = self._definition.get("transform")
        self._state = None
        self._device_info = {
            "identifiers": {(DOMAIN, "OpenWB")},
            "name": "OpenWB",
            "manufacturer": "OpenWB",
        }

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""

            if self._transform is not None:
                self._state = self._transform(message.payload)
            else:
                self._state = message.payload

            self.async_write_ha_state()

        _LOGGER.info("openWB topic: " + self._topic)
        await mqtt.async_subscribe(self.hass, self._topic, message_received, 1)

    @property
    def name(self):
        """Return the name of the sensor supplied in constructor."""
        return self._name

    @property
    def unique_id(self) -> Optional[str]:
        return self._unique_id

    @property
    def state(self):
        """Return the current state of the entity."""
        return self._state

    @property
    def device_class(self):
        """Return the device_class of this sensor."""
        return self._device_class

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of this sensor."""
        return self._unit_of_measurement

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enable_default

    @property
    def icon(self):
        """Return the icon of this sensor."""
        return self._icon

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info