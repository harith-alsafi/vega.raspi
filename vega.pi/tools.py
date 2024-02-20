class VegaTools:
    def __init__(self):
        self._pi = pigpio.pi()

    def set_gpio(self, gpio, value):
        self._pi.write(gpio, value)

    def get_gpio(self, gpio):
        return self._pi.read(gpio)

    def cleanup(self):
        self._pi.stop()