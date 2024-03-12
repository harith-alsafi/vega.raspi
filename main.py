from typing import List, Optional
from vegapi import Vega, Device, RunTool, SinglePlot , ToolResult, tools_to_json 
import RPi.GPIO as GPIO
import json 
import drivers
from picamera2 import Picamera2
import pyimgur
import datetime
import time
import psutil
from tabulate import tabulate
from vegapi.database import DataPlot, DataSeries, PeriodicData
import Adafruit_DHT

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

def get_temp_humidity() -> tuple[float, float]:
   sensor = Adafruit_DHT.DHT11
   pin = 4
   humidity, temperature = Adafruit_DHT.read(sensor, pin)
   return (temperature, humidity)

def find_device(name: str) -> Optional[Device]:
   for device in devices:
      if device.name.lower() == name.lower():
         return device
   return None

def led_call(value: bool, pin: int) -> Optional[str]:
   if value:
      GPIO.output(pin, GPIO.HIGH)
   else:
      GPIO.output(pin, GPIO.LOW)
   return None

def ultrasonic_call() -> float:
   # start the pulse to get the sensor to send the ping
   # set trigger pin low for 2 micro seconds
   GPIO.output(23, 0)
   time.sleep(2E-6)
   # set trigger pin high for 10 micro seconds
   GPIO.output(23, 1)
   time.sleep(10E-6)
   # go back to zero - communication compete to send ping
   GPIO.output(23, 0)
   # now need to wait till echo pin goes high to start the timer
   # this means the ping has been sent
   while GPIO.input(24) == 0:
      pass
   echoStartTime = time.time()
   while GPIO.input(24) == 1:
      pass
   echoStopTime = time.time()
   pingTravelTime = echoStopTime - echoStartTime
   dist_cm = (pingTravelTime*34444)/2
   return dist_cm

led1 = Device(name="LED1", description="Yellow LED light", value=False, pins=["17"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 17))
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW) 

led2 = Device(name="LED2", description="Red LED light", value=False, pins=["27"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 27))
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW) 

led3 = Device(name="LED3", description="Blue LED light", value=False, pins=["22"], device_type="digital", isInput=False, onCall=lambda x: led_call(x, 22))
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

lcd = Device(name="LCD", description="LCD display 16x4 with blue backlit", value="Hello World", pins=["SDA", "SCL"], device_type="i2c", isInput=False)
display = drivers.Lcd()

# set up motor circuit + pins
motor = Device(name="MTR", description="Motor", value=0.0, pins=["5", "6"], device_type="pwm", isInput=False, onCall=lambda x: 0.0)

# set up buzzer circuit + pins
buzzer = Device(name="BZR", description="Buzzer", value=0.0, pins=["12"], device_type="pwm", isInput=False, onCall=lambda x: 0.0)

camera = Device(name="CAM", description="Raspberry Pi Camera", value="none", pins=["PI-CAM"], device_type="i2c", isInput=False)
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
CLIENT_ID = "d84708345365a2b"
im = pyimgur.Imgur(CLIENT_ID)

ultrasonic = Device(name="ULTS", description="Ultrasonic distance sensor in cm", value=0.0, pins=["23", "24"], device_type="analog", isInput=True, onCall=lambda x: ultrasonic_call())
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN)

# set up circuit + pins for DHT11
temperature = Device(name="TMP", description="Temperature sensor part of DHT11", value=0.0, pins=["4"], device_type="analog", isInput=True, onCall=lambda x: get_temp_humidity()[0])

humidity = Device(name="HDT", description="Humidity sensor part of DHT11", value=0.0, pins=["4"], device_type="analog", isInput=True, onCall=lambda x: get_temp_humidity()[1])

# set up light sensor circuit + pins use LDR + capacitor
light = Device(name="LGT", description="Light sensor", value=0.0, pins=["18"], device_type="analog", isInput=True, onCall=lambda x: 0.0)

# set up infrared sensor circuit + pins
infrared = Device(name="IR", description="Infrared sensor", value=True, pins=["25"], device_type="digital", isInput=True, onCall=lambda x: True)

devices: List[Device] = [led1, led2, led3, lcd, camera, ultrasonic, temperature, humidity]

def get_devices(names: Optional[list[str]] = None) -> list[Device]:
   for device in devices:
      if device.isInput == False:
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
            results.append(toolCall)
         elif tool.name == "print_lcd":
            text = argJson["text"]
            print_lcd(text)
            toolCall = ToolResult(name=tool.name, result="LCD is now " + text)
            results.append(toolCall)
         elif tool.name == "capture_image":
            url = capture_image()
            toolCall = ToolResult(name=tool.name, result="Image has been captured and uploaded", ui="image", data=url)
            results.append(toolCall)
         elif tool.name == "get_stats":
            stats = get_stats()
            toolCall = ToolResult(name=tool.name, result="Extracted the CPU, RAM, disk and uptime", ui="table", data=stats)
            results.append(toolCall)
         elif tool.name == "get_sensor_data":
            sensorNames = argJson["sensorNames"]
            interval = argJson["interval"]
            data = get_sensor_data(sensorNames, interval)
            toolCall = ToolResult(name=tool.name, result="Extracted the sensor data", ui="plot", data=data)
            results.append(toolCall)
         elif tool.name == "get_devices":
            deviceNames = argJson["deviceNames"]
            devices = get_devices(deviceNames)
            toolCall = ToolResult(name=tool.name, result="Extracted the devices data", ui="cards", data=devices)
            results.append(toolCall)
      return results
   return [
   
   ]

def every_period() -> List[PeriodicData]:
   data: List[PeriodicData] = []
   for device in devices:
      if device.isInput:
         device.run_call(None)
         data.append(PeriodicData(name=device.name, y=device.value))
   return data

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
   device:Device = find_device(name)
   if device:
      # convert value from string to boolean 
      boolVal = value.lower() == "true" or value == "1" or value == "on"
      device.run_call(boolVal)
      device.value = boolVal
      return 1

@vega.add_tool(
   description="Gets array of sensor data", 
   parameter_description={
      "sensorNames": "List of sensors to get the data of given in comma seperated format, for example it can be 'SENSOR1, SENSOR2' it is optional so when not given it will fetch all the devices",
      "interval": "Interval in seconds to get the data, for example last 300 seconds"
   }
)
def get_sensor_data(sensorNames: str, interval: str) -> DataPlot:
   if "," in sensorNames:
      sensorNames = devices.split(",")
      devicesList: List[Device] = []
      data: List[DataSeries] = []
      for sensorName in sensorNames:
         device = find_device(sensorName)
         if device and device.isInput:
            deviceData = vega.get_data_series_by_period(sensorName, interval)
            data.append(DataSeries(name=sensorName, data=deviceData))
      plot = DataPlot(title=sensorNames, x_label="Time (s)", y_label="Values")
      return plot
   elif sensorNames != "" and sensorNames.lower() != "all" and sensorNames != " ":
      device = find_device(sensorNames)
      if device and device.isInput:
         deviceData = vega.get_data_series_by_period(sensorNames, interval)
         data = [DataSeries(name=sensorNames, data=deviceData)]
         plot = DataPlot(title=sensorNames, x_label="Time (s)", y_label="Values")
         return plot
   else:
      data: List[DataSeries] = []
      for device in devices:
         if device.isInput:
            deviceData = vega.get_data_series_by_period(device.name, interval)
            data.append(DataSeries(name=device.name, data=deviceData))
      plot = DataPlot(title="All Sensors", x_label="Time (s)", y_label="Values")


@vega.add_tool(
   description="Gets the information of the raspberry pi such as RAM, CPU, etc.", 
)
def get_stats() -> str:
   # Collect data
   cpu_temp = 'N/A'
   try:
      with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
         temp = f.read().strip()
         cpu_temp = f'{float(temp) / 1000:.2f} °C'
   except FileNotFoundError:
      cpu_temp = 'N/A'
   cpu_usage = f'{psutil.cpu_percent(interval=1):.2f} %'
   ram = psutil.virtual_memory()
   ram_usage = f'{ram.percent:.2f} %'
   disk = psutil.disk_usage('/')
   disk_usage =  f'{disk.percent:.2f} %'
   uptime = psutil.boot_time()
   uptime = f'Uptime: {round(time.time() - uptime)} seconds'
   # Create Markdown table
   table_data = [
      ['CPU Temperature', cpu_temp],
      ['CPU Usage', cpu_usage],
      ['RAM Usage', ram_usage],
      ['Disk Usage', disk_usage],
      ['Uptime', uptime]
   ]
   markdown_table = tabulate(table_data, headers=['Metric', 'Value'], tablefmt='pipe')
   return markdown_table


@vega.add_tool(
   description="Prints the text on the LCD screen", 
   parameter_description={
      "text": "Text to print on the LCD screen"
   }
)
def print_lcd(text: str):
   display.lcd_clear()
   display.lcd_display_string(text, 1) 
   lcd.value = text

@vega.add_tool(
   description="Captures an image from the raspberry pi camera and returns the URL", 
)
def capture_image() -> str:
   imgName = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
   imgPath = "images/" + imgName + ".jpg"
   picam2.start()
   picam2.capture_array()
   picam2.capture_file(imgPath)
   picam2.stop()
   uploaded_image = im.upload_image(path=imgPath, title=imgName)
   camera.value = uploaded_image.link
   return uploaded_image.link

@vega.add_tool(
   description="Gets information of the devices",
   parameter_description={
      "deviceNames": "List of devices to get the status of given in comma seperated format, for example it can be 'LED1, LED2' it is optional so when not given it will fetch all the devices"
   }
)
def get_devices(deviceNames: str) -> List[Device]:
   if "," in deviceNames:
      deviceNames = devices.split(",")
      devicesList: List[Device] = []
      for deviceName in deviceNames:
         device = find_device(deviceName)
         if device:
            if device.isInput == False:
               device.run_call(None)
            devicesList.append(device)
      return devicesList
   elif deviceNames != "" and deviceNames != "all" and deviceNames != " ":
      device = find_device(deviceNames)
      if device:
         if device.isInput == False:
            device.run_call(None)
      return [device]
   else:
      for device in devices:
         if device.isInput == False:
            device.run_call(None)
      return devices

vega.run()
vega.start_recording()

print(tools_to_json(vega.tools))

while True:
   pass