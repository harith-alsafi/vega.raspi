import json
from typing import Literal, Optional, Generic, TypeVar, List

device_types = Literal[
    "pwm",
    "digital",
    "analog",
    "i2c"
];

# Define a generic type variable
T = TypeVar('T')

class Device(Generic[T]):
    name: str
    description: str
    pins: List[int]
    device_type: device_types
    isInput: bool # True if input, False if output
    isConnected: bool # True if connected, False if connected
    value: T
    frequency: Optional[float]

    def __init__(self, name: str, description: str, pins: List[int], device_type: device_types, isInput: bool, value: T, frequency: Optional[float] = None, isConnected: bool = True):
        self.name = name
        self.description = description
        self.pins = pins
        self.device_type = device_type
        self.isInput = isInput
        self.value = value 
        self.frequency = frequency
        self.isConnected = isConnected

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value.__str__(),
            "type": self.device_type,
            "pins": self.pins,
            "isInput": self.isInput,
            "isConnected": self.isConnected,
            "frequency": self.frequency,
        }


def devices_to_json(devices: List[Device]):
    return json.dumps([device.to_json() for device in devices], indent=4)
