"""PowerDog"""
from __future__ import annotations
import logging

from typing import TYPE_CHECKING
from datetime import timedelta
import xmlrpc.client

import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from powerdog import powerdog_api
from powerdog.powerdog_sensor import (
    Sensor,
    SensorType,
    UndefinedSensorTypeException,
    Unit,
)

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMA sensors."""
    email = hass.data[DOMAIN][CONF_EMAIL]
    password = hass.data[DOMAIN][CONF_PASSWORD]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.unique_id)},
        manufacturer="eco data",
        name="powerdog",
    )

    sensors = []
    apikey = powerdog_api.get_apikey(email, password)
    powerdog_ids = powerdog_api.get_powerdog_ids(apikey)
    for powerdog_id in powerdog_ids:
        inverter_ids = powerdog_api.get_inverter_ids(apikey, powerdog_id)
        types = [SensorType.PAC, SensorType.PDC, SensorType.UDC]
        for id_i in inverter_ids:
            for type_i in types:
                coordinator = CoordinatorEntity(hass, type_i)
                sensors.append(Sensor(id=id_i, type=type_i, coordinator=coordinator))

        types = [
            SensorType.PURCHASE,
            SensorType.DELIVERY,
            SensorType.GENERATION,
            SensorType.CONSUMPTION,
        ]
        for type_i in types:
            id_i = powerdog_api.get_counter(apikey, powerdog_id, type_i)
            sensors.append(
                Sensor(
                    id=id_i, type=type_i, coordinator=CoordinatorEntity(hass, type_i)
                )
            )

    if TYPE_CHECKING:
        assert config_entry.unique_id

    entities = []
    for sensor in sensors:
        entities.append(
            PowerdogSensor(
                config_entry.unique_id,
                device_info,
                sensor,
            )
        )

    async_add_entities(entities)


class PowerdogSensor(CoordinatorEntity, SensorEntity):
    """Representation of a PowerDog sensor."""

    def __init__(
        self,
        config_entry_unique_id: str,
        device_info: DeviceInfo,
        sensor: Sensor,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(sensor.coordinator)
        self._sensor = sensor
        self._config_entry_unique_id = config_entry_unique_id
        self._attr_device_info = device_info

        if self.native_unit_of_measurement == Unit.UNDEFINED:
            raise UndefinedSensorTypeException()
        if self.native_unit_of_measurement == Unit.ENERGY_KILO_WATT_HOUR:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_device_class = SensorDeviceClass.ENERGY
        if self.native_unit_of_measurement == Unit.POWER_WATT:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_device_class = SensorDeviceClass.POWER
        if self.native_unit_of_measurement == Unit.TEMPERATURE:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self._attr_device_info is None or not (
            name_prefix := self._attr_device_info.get("name")
        ):
            name_prefix = "Powerdog"

        return f"{name_prefix} {self._sensor.type}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._sensor.value

    @property
    def native_unit_of_measurement(self) -> Unit:
        """Return the unit the value is expressed in."""
        return self._sensor.unit

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this sensor."""
        return f"{self._config_entry_unique_id}_{self._sensor.id}"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()


class PowerdogCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, my_api, sensor_type):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="powerdog",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )
        self.my_api = my_api
        self.sensor_type = sensor_type

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self.my_api.fetch_data()
        except xmlrpc.client.Fault(100, "Authentication failed") as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except powerdog_api.APICallResultInvalidException() as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
