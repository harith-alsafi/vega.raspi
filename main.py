from typing import Optional
from vegapi import Vega, Device, RunTool, DataSeries, ToolResult, run_tools_to_json

led1 = Device(name="LED1", description="Yellow LED light", value=True, pins=["0"], device_type="digital", isInput=False)

led2 = Device(name="LED2", description="Red LED light", value=True, pins=["1"], device_type="digital", isInput=False)

led3 = Device(name="LED3", description="Blue LED light", value=True, pins=["2"], device_type="digital", isInput=False)

lcd = Device(name="LCD", description="LCD display 20x4", value="Hello World", pins=["3"], device_type="i2c", isInput=False)

camera = Device(name="Camera", description="Raspberry Pi Camera", value="none", pins=["4"], device_type="i2c", isInput=False)

def get_devices(names: Optional[list[str]] = None) -> list[Device]:
   return [
   
   ]

def run_tools(tools: list[RunTool]) -> list[ToolResult]:
   return [
   
   ]

def every_period() -> list[DataSeries]:
   return [
      
   ]

vega = Vega(onGetDevices=get_devices, onRunTools=run_tools, onEveryPeriod=every_period, period=2)

@vega.add_tool(
    description="Sets the LED name on or off. ", 
    parameter_description={
      "name": "name of the LED ex: LED1",                  
      "value": "True for on, False for off."
   }
)
def set_led(name: str, value: bool) -> int:
   pass

@vega.add_tool(
   description="Gets array of sensor data", 
   parameter_description={
      "name": "name of the Sensor ex: SENSOR1",
      "interval": "Interval in seconds to get the data, for example last 300 seconds"
   }
)
def get_sensor_data(name: str, interval: int) -> float:
   pass

@vega.add_tool(
   description="Gets the information of the raspberry pi such as RAM, CPU, etc.", 
)
def get_stats():
   pass

@vega.add_tool(
   description="Prints the text on the LCD screen", 
   parameter_description={
      "text": "Text to print on the LCD screen"
   }
)
def print_lcd(text: str):
   pass

@vega.add_tool(
   description="Captures an image from the raspberry pi camera", 
)
def capture_image():
   pass