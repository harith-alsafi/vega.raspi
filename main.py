from typing import List, Optional
from vegapi import Vega, Device, RunTool, DataSeries, ToolResult, tools_to_json
import RPi.GPIO as GPIO
import json 
import drivers

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

def led_call(value: bool, pin: int) -> Optional[str]:
   if value:
      GPIO.output(pin, GPIO.HIGH)
   else:
      GPIO.output(pin, GPIO.LOW)
   return None

led1 = Device(name="LED1", description="Yellow LED light", value=False, pins=["17"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 17))
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW) 

led2 = Device(name="LED2", description="Red LED light", value=False, pins=["27"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 27))
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW) 

led3 = Device(name="LED3", description="Blue LED light", value=False, pins=["22"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 22))
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

lcd = Device(name="LCD", description="LCD display 20x4", value="Hello World", pins=["3"], device_type="i2c", isInput=False)
display = drivers.Lcd()

camera = Device(name="Camera", description="Raspberry Pi Camera", value="none", pins=["4"], device_type="i2c", isInput=False)

devices: List[Device] = [led1, led2, led3, lcd, camera]

def get_devices(names: Optional[list[str]] = None) -> list[Device]:
   for device in devices:
      if device.isInput:
         device.run_call(None)
      return devices

def run_tools(tools: list[RunTool]) -> list[ToolResult]:
   if tools:
      results = []
      for tool in tools:
         argJson = json.loads(tool.arguments)
         if tool.name == "set_led":
            ledName =  argJson["name"]
            value = argJson["value"]
            set_led(ledName, value)
            toolCall = ToolResult(name=tool.name, result="LED is now " + value)
            print(toolCall.to_json())
            results.append(toolCall)
         elif tool.name == "print_lcd":
            text = argJson["text"]
            print_lcd(text)
            toolCall = ToolResult(name=tool.name, result="LCD is now " + text)
            print(toolCall.to_json())
            results.append(toolCall)
         elif tool.name == "capture_image":
            pass
      return results
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
def set_led(name: str, value: str) -> int:
   # find the device from devices list using the name
   device:Device = [device for device in devices if device.name == name][0]
   if device:
      # convert value from string to boolean 
      boolVal = value.lower() == "true" or value == "1" or value == "on"
      device.run_call(boolVal)
      return 1

@vega.add_tool(
   description="Gets array of sensor data", 
   parameter_description={
      "name": "name of the Sensor ex: SENSOR1",
      "interval": "Interval in seconds to get the data, for example last 300 seconds"
   }
)
def get_sensor_data(name: str, interval: str) -> float:
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
   display.lcd_clear()
   display.lcd_display_string(text, 1) 

@vega.add_tool(
   description="Captures an image from the raspberry pi camera", 
)
def capture_image():
   pass


@vega.add_tool(
   description="Gets the status of the devices",
   parameter_description={
      "devices": "List of devices to get the status of given in comma seperated format, for example it can be 'LED1, LED2' it is optional so when not given it will fetch all the devices"
   }
)
def get_devices_status(devices: str):
   pass

vega.run()


print(tools_to_json(vega.tools))

while True:
   pass