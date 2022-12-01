"""PowerDog api service"""
import xmlrpc.client
import hashlib
from powerdog.powerdog_sensor import SensorType

XMLRPCclient = xmlrpc.client.ServerProxy("https://api.power-dog.eu/index.php")
PRINT_RESPONSE_OUTPUT = True


class APICallResultInvalidException(BaseException):
    """Raised when the API call result is invalid"""


class NoItemFoundException(BaseException):
    """Raised when no item was found"""


def hash_password(password: str) -> str:
    """Hashing the password string"""
    result = hashlib.md5(password.encode())
    print("Hash Value: ", end="")
    print(result.hexdigest())
    return result.hexdigest()


def get_apikey(email: str, password: str):
    """Fetching the apikey"""
    with XMLRPCclient as proxy:
        response = proxy.getApiKey(email, hash_password(password))
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            return response["apikey"]
        else:
            raise APICallResultInvalidException("getApiKey failed")


def get_powerdog_ids(apikey: str):
    """Fetching the powerdog ids"""
    with XMLRPCclient as proxy:
        response = proxy.getPowerDogs(apikey)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            if not response["powerdogs"]:
                return []
            else:
                return [value["id"] for value in response["powerdogs"]]
        else:
            raise APICallResultInvalidException("getPowerDogs failed")


def get_powerdog_uids(apikey: str):
    """Fetching the powerdog uids"""
    with XMLRPCclient as proxy:
        response = proxy.getPowerDogs(apikey)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            uids = []
            for powerdog in response["powerdogs"]:
                uids.append(powerdog["uid"])
            return uids
        else:
            raise APICallResultInvalidException("getPowerDogs failed")


def get_inverter_ids(apikey: str, powerdog_id: str):
    """Fetching the inverter ids"""
    with XMLRPCclient as proxy:
        response = proxy.getInverters(apikey, powerdog_id)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            if not response["inverters"]:
                return []
            else:
                return [value["id"] for value in response["inverters"].values()]
        else:
            raise APICallResultInvalidException("getInverters failed")


def get_sensor_ids(apikey: str, powerdog_id: str):
    """Fetching the sensor ids"""
    with XMLRPCclient as proxy:
        response = proxy.getSensors(apikey, powerdog_id)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            if not response["sensors"]:
                return []
            else:
                return [value["id"] for value in response["sensors"].values()]
        else:
            raise APICallResultInvalidException("getSensors failed")


def get_counter_ids(apikey: str, powerdog_id: str):
    """Fetching the counter ids"""
    with XMLRPCclient as proxy:
        response = proxy.getCounters(apikey, powerdog_id)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            if not response["counters"]:
                return []
            else:
                return [value["id"] for value in response["counters"].values()]
        else:
            raise APICallResultInvalidException("getCounters failed")


def get_counter(apikey: str, powerdog_id: str, sensor_type: SensorType):
    """Fetching the sensor id for type"""
    with XMLRPCclient as proxy:
        response = proxy.getCounters(apikey, powerdog_id)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            if not response["counters"]:
                return []
            else:
                for value in response["counters"].values():
                    switch = {
                        SensorType.PURCHASE: "Bezug",
                        SensorType.DELIVERY: "Lieferung",
                        SensorType.GENERATION: "PV ANLAGE",
                        SensorType.CONSUMPTION: "Eigenverbrauch",
                    }
                    if value["Name"] == switch.get(sensor_type, SensorType.UNDEFINED):
                        return value
        else:
            raise APICallResultInvalidException("getSensors failed")


def get_sensor_data(apikey: str, sensor_id: str, timestamp_from, timestamp_to):
    """Fetching the sensors/counters data"""
    with XMLRPCclient as proxy:
        response = proxy.getSensorData(apikey, sensor_id, timestamp_from, timestamp_to)
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            return list(response["datasets"].values())
        else:
            raise APICallResultInvalidException("getCounters failed")


def get_string_data(
    apikey: str, sensor_id: str, string_num: int, timestamp_from, timestamp_to
):
    """Fetching the inverter ids"""
    with XMLRPCclient as proxy:
        response = proxy.getStringData(
            apikey, sensor_id, string_num, timestamp_from, timestamp_to
        )
        if response["valid"] == 1:
            if PRINT_RESPONSE_OUTPUT:
                print(response)
            return list(response["datasets"].values())
        else:
            raise APICallResultInvalidException("getCounters failed")
