from typing import Literal

component_types = Literal["sensor", "led", "motor", "relay", "button", "switch", "potentiometer", "encoder", "lcd", "buzzer", "fan", "heater", "pump", "valve", "speaker", "microphone", "camera", "display", "touchscreen", "gyroscope", "accelerometer", "magnetometer", "gps", "rfid", "nfc", "bluetooth", "wifi", "ethernet", "usb", "can", "spi", "i2c", "uart", "gpio", "adc", "dac", "pwm", "interrupt", "timer", "counter", "watchdog", "rtc", "memory", "storage", "processor", "microcontroller", "microprocessor", "fpga", "asic", "soc", "gpu", "dsp", "fpu", "cpu", "ram", "rom", "flash"]

pin_types = Literal["input", "output"]

class Component:
    name: str
    description: str
    pin: int
    component_type: component_types
    pin_input: bool # True if input, False if output
    value: float
    status: bool # True if on, False if off

    def __init__(self) -> None:
        pass

    def set_value(self, value: float):
        self.value = value

    def set_status(self, status: bool):
        self.status = status

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "type": self.component_type,
            "pin": self.pin
        }


class VegaComponent:
    def __init__(self, name, value, unit, min, max, step, default):
        self.name = name
        self.value = value
        self.unit = unit
        self.min = min
        self.max = max
        self.step = step
        self.default = default

    def __str__(self):
        return f"{self.name}={self.value}{self.unit} ({self.min}-{self.max}, step={self.step}, default={self.default})"

    def __repr__(self):
        return f"PiComponent({self.name}, {self.value}, {self.unit}, {self.min}, {self.max}, {self.step}, {self.default})"

    def set(self, value):
        if value < self.min:
            self.value = self.min
        elif value > self.max:
            self.value = self.max
        else:
            self.value = value

    def reset(self):
        self.value = self.default

    def increase(self):
        self.set(self.value + self.step)

    def decrease(self):
        self.set(self.value - self.step)

    def get(self):
        return self.value

    def get_default(self):
        return self.default

    def get_min(self):
        return self.min

    def get_max(self):
        return self.max

    def get_step(self):
        return self.step

    def get_unit(self):
        return self.unit

    def get_name(self):
        return self.name