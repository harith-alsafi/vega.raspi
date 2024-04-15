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
from vegapi.api import MapTool
from vegapi.database import DataPlot, DataSeries, PeriodicData
import time
import adafruit_dht
import board
import serial               #import serial pacakge
import sys   
import pigpio


GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

def find_device(name: str) -> Optional[Device]:
   for device in devices:
      if device.name.lower() == name.lower():
         return device
   return None

## OUTPUTS
def set_pin(value: bool, pin: int) -> None:
   if value:
      GPIO.output(pin, GPIO.HIGH)
   else:
      GPIO.output(pin, GPIO.LOW)

led1 = Device(name="LED1", description="Yellow LED light", value=False, pins=["17"], device_type="digital", isInput=False, onCall=lambda x: set_pin(x, 17))
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW) 

led2 = Device(name="LED2", description="Red LED light", value=False, pins=["27"], device_type="digital", isInput=False, onCall=lambda x: set_pin(x, 27))
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW) 

led3 = Device(name="LED3", description="Blue LED light", value=False, pins=["22"], device_type="digital", isInput=False, onCall=lambda x: set_pin(x, 22))
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

lcd = Device(name="LCD", description="LCD display 16x4 with blue backlit", value="Hello World", pins=["SDA", "SCL"], device_type="i2c", isInput=False)
display = drivers.Lcd()

## SERVO MOTOR
servo = Device(name="SRV", description="Servo Motor", value=0.0, pins=["13"], device_type="pwm", isInput=False, onCall=lambda x: 0.0)
servo_pin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin,GPIO.OUT)
servo_pwm = pigpio.pi()
servo_pwm.set_mode(servo, pigpio.OUTPUT)
servo_pwm.set_PWM_frequency( servo, 50 )
def SetAngle(angle):
   pulse_width = (angle / 180.0) * (2500 - 500) + 500
   servo_pwm.set_servo_pulsewidth(servo, pulse_width)
   time.sleep(3)  # Adjust this delay as needed

## FAN
fan = Device(name="FAN", description="On off Fan connected to a 5v relay", value=False, pins=["12"], device_type="digital", isInput=False, onCall=lambda x: set_pin(x, 12))
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)

## CAMERA
camera = Device(name="CAM", description="Raspberry Pi Camera", value="none", pins=["PI-CAM"], device_type="i2c", isInput=False)
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
CLIENT_ID = "d84708345365a2b"
im = pyimgur.Imgur(CLIENT_ID)

## ULTRASONIC
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN)
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
ultrasonic = Device(name="ULTS", description="Ultrasonic distance sensor in cm", value=0.0, pins=["23", "24"], device_type="analog", isInput=True, onCall=lambda x: ultrasonic_call())

## TEMP
dht_device = adafruit_dht.DHT11(board.D4)
def get_temp() -> Optional[float]:
   try:
      temperature_c =  dht_device.temperature
      if temperature_c:
         return float(temperature_c)
      return temperature_c
   except RuntimeError as err:
      return None
temperature = Device(name="TMP", description="Temperature sensor part of DHT11", value=0.0, pins=["4"], device_type="analog", isInput=True, onCall=lambda x: get_temp())

## HUMIDITY
def get_humidity() -> Optional[float]:
   try:
      humidity =  dht_device.humidity
      if humidity:
         return float(humidity)
      return humidity
   except RuntimeError as err:
      return None
humidity = Device(name="HDT", description="Humidity sensor part of DHT11", value=0.0, pins=["4"], device_type="analog", isInput=True, onCall=lambda x: get_humidity())

## BUTTON 
def get_button() -> bool:
   pass
button_gpio = 5
GPIO.setup(button_gpio, GPIO.IN)
button_status = False
button_count = 0
button = Device(name="BTN", description="Button which toggles states, starting by false and also has a counter for how many times it was clicked", value=False, pins=["5"], device_type="digital", isInput=True, onCall=lambda x: button_status)

## GPS
gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyS0")              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
gps = Device(name="GPS", description="GPS module", value="none", pins=["15"], device_type="serial", isInput=False, onCall=lambda x: True)
def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    
    print("NMEA Time: ", nmea_time,'\n')
    print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    
    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation
    
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

devices: List[Device] = [led1, led2, led3, lcd,  camera, ultrasonic, temperature, humidity, gps, servo, fan]

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
         elif tool.name == "get_raspberry_stats":
            stats = get_raspberry_stats()
            toolCall = ToolResult(name=tool.name, result="Extracted the CPU, RAM, disk and uptime", ui="table", data=stats)
            results.append(toolCall)
         elif tool.name == "get_recorded_data":
            sensorNames = argJson["sensorNames"]
            interval = argJson["interval"]
            data: DataPlot = get_recorded_data(sensorNames, interval)
            print(data.to_json())
            toolCall = ToolResult(name=tool.name, result="ONLY Inform the user that the plot is shown above", ui="plot", data=data.to_json())
            results.append(toolCall)
         elif tool.name == "get_devices":
            deviceNames = argJson["deviceNames"]
            devices: List[Device] = get_devices(deviceNames)
            arrayString = [device.to_json() for device in devices]
            toolCall = ToolResult(name=tool.name, result="ONLY Inform the user that the connect devices will be shown above", ui="cards", data=arrayString)
            results.append(toolCall)
         elif tool.name == "get_location":
            location = get_location()
            toolCall = ToolResult(name=tool.name, result="ONLY Inform the user that the location will be shown above", ui="map", data=location.to_json())
            results.append(toolCall)
         elif tool.name == "set_servo_angles":
            angles = argJson["angles"]
            output = set_servo_angles(angles)
            toolCall = ToolResult(name=tool.name, result="Servo has been set to the given angles", data=output)
            results.append(toolCall)
         elif tool.name == "set_fan":
            value = argJson["value"]
            set_fan(value)
            toolCall = ToolResult(name=tool.name, result="Fan is now " + value)
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
    description="Sets the fan on or off. ", 
    parameter_description={
      "value": "True for on, False for off."
   }
)
def set_fan(value: str):
   boolVal = value.lower() == "true" or value == "1" or value == "on"
   fan.run_call(boolVal)
   fan.value = boolVal


@vega.add_tool(
   description="Gets recorded data of sensor over a period of time", 
   parameter_description={
      "sensorNames": "List of sensors to get the data of given in comma seperated format, for example it can be 'SENSOR1, SENSOR2' it is optional so when not given it will fetch all the devices",
      "interval": "Interval in seconds to get the data, for example last 300 seconds"
   }
)
def get_recorded_data(sensorNames: str, interval: str) -> DataPlot:
   seconds = int(interval)
   if "," in sensorNames:
      sensorNamesArray = sensorNames.split(",")

      data: List[DataSeries] = []
      for sensorName in sensorNamesArray:
         sensor = sensorName.strip()
         device = find_device(sensor)
         if device and device.isInput:
            deviceData = vega.get_all_data_series_by_seconds(sensor, seconds)
            data.append(DataSeries(name=sensor, data=deviceData))
      plot = DataPlot(title=sensorNames, x_label="Time (s)", y_label="Values", data=data)
      return plot
   elif sensorNames != "" and sensorNames.lower() != "all" and sensorNames != " ":
      device = find_device(sensorNames)
      if device and device.isInput:
         deviceData = vega.get_all_data_series_by_seconds(sensorNames, seconds)
         data = [DataSeries(name=sensorNames, data=deviceData)]
         plot = DataPlot(title=sensorNames, x_label="Time (s)", y_label="Values", data=data)
         return plot
   else:
      data: List[DataSeries] = []
      for device in devices:
         if device.isInput:
            deviceData = vega.get_all_data_series_by_seconds(device.name, seconds)
            data.append(DataSeries(name=device.name, data=deviceData))
      plot = DataPlot(title="All Sensors", x_label="Time (s)", y_label="Values", data=data)
      return plot

@vega.add_tool(
   description="Gets the information of the raspberry pi such as RAM, CPU, etc.", 
)
def get_raspberry_stats() -> str:
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
   description="Gets the list of connected devices using deviceNames and their information, this is also used to fetch data from certain devices",
   parameter_description={
      "deviceNames": "List of devices to get the information of or fetch data from, given in comma seperated format, for example it can be 'TMP, LED2' (this is optional so when not given it will fetch all the devices)"
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

@vega.add_tool(
   description="Gets location using longitude and latitude from GPS module",
)
def get_location() -> MapTool:
   received_data = (str)(ser.readline())                   #read NMEA string received
   GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string 
   if (GPGGA_data_available>0):
      GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
      NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
      GPS_Info()                                          #get time, latitude, longitude]
      gps.value = "Latitude: " + lat_in_degrees + " Longitude: " + long_in_degrees
      return MapTool(longitude=long_in_degrees, latitude=lat_in_degrees)
   gps.value = "Latitude: " + lat_in_degrees + " Longitude: " + long_in_degrees
   return MapTool(longitude=-1.5547755416554814, latitude=53.809666674924046)

@vega.add_tool(
   description="Sets the servo to a given set of angles between 0 and 180",
   parameter_description={
      "angles": "List of angles to set the servo, given in comma seperated format, for example it can be '0, 180, 0' which will set the servo to be 0 at first, then at 180 then 0 again with each angle being set for 1 second."
   }
)
def set_servo_angles(angles: str) -> str:
   if "," in angles:
      angles = angles.split(",")
      for angle in angles:
         SetAngle(int(angle))
      return "Success"
   return "No angle given"

vega.run()
vega.delete_all_data_series()
vega.start_recording()

print(tools_to_json(vega.tools))

status = True
while status:
   button_status = GPIO.input(button_gpio)
   if button_status:
      button_count += 1
servo_pwm.set_PWM_dutycycle( servo, 0 )
servo_pwm.set_PWM_frequency( servo, 0 )
GPIO.cleanup()