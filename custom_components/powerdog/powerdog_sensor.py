"""PowerDog sensor class"""
from enum import Enum
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class SensorType(Enum):
    """Type of the PowerDog sensor"""

    PAC = "PAC"
    PDC = "PDC"
    UDC = "UDC"
    TEMPERATURE = "Temperature"
    PURCHASE = "Purchase"
    DELIVERY = "Delivery"
    GENERATION = "Generation"
    CONSUMPTION = "Consumption"
    UNDEFINED = "UNDEFINED"


class Unit(Enum):
    """Unit enumeration"""

    ENERGY_KILO_WATT_HOUR = "kWh"
    POWER_WATT = "W"
    TEMPERATURE = "°C"
    UNDEFINED = "UNDEFINED"


class Sensor:
    """PowerDog sensor class"""

    id: str
    type: SensorType
    coordinator: DataUpdateCoordinator

    @property
    def unit(self) -> Unit:
        """Return the unit of this sensor."""
        switch = {
            SensorType.PAC: Unit.ENERGY_KILO_WATT_HOUR,
            SensorType.PDC: Unit.ENERGY_KILO_WATT_HOUR,
            SensorType.UDC: Unit.ENERGY_KILO_WATT_HOUR,
            SensorType.TEMPERATURE: Unit.TEMPERATURE,
            SensorType.PURCHASE: Unit.POWER_WATT,
            SensorType.DELIVERY: Unit.POWER_WATT,
            SensorType.GENERATION: Unit.POWER_WATT,
            SensorType.CONSUMPTION: Unit.POWER_WATT,
        }
        return switch.get(type, Unit.UNDEFINED)


class UndefinedSensorTypeException(Exception):
    """UndefinedSensorType error"""
