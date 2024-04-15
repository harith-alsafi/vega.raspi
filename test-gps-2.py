import serial               #import serial pacakge
from time import sleep
import sys                  #import system package


gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyS0")              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
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

class MapTool:
    longitude: str;
    latitude: str;
    def __init__(self, longitude: str, latitude: str):
        self.longitude = longitude
        self.latitude = latitude
    
    def to_json(self):
        return {
            "longitude": self.longitude,
            "latitude": self.latitude
        }

def get_location() -> MapTool:
   received_data = (str)(ser.readline())                   #read NMEA string received
   GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string 
   if (GPGGA_data_available>0):
      GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
      NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
      GPS_Info()                                          #get time, latitude, longitude]
      return MapTool(longitude=long_in_degrees, latitude=lat_in_degrees)
   return MapTool(longitude=-1.5547106082858528, latitude=53.80978957968428)
loc = get_location()
print(loc.to_json())