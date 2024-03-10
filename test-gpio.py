import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

GPIO.setup(23, GPIO.IN) # Set pin 8 to be an output pin and set initial value to low (off)

def toggle_leds():
   GPIO.output(17, GPIO.HIGH) # Turn on
   GPIO.output(27, GPIO.HIGH) # Turn on
   GPIO.output(22, GPIO.HIGH) # Turn on

   sleep(1) # Sleep for 1 second
   GPIO.output(17, GPIO.LOW) # Turn off
   GPIO.output(27, GPIO.LOW) # Turn off
   GPIO.output(22, GPIO.LOW) # Turn off

while True: # Run forever
   data = GPIO.input(23)
   print(data)
   sleep(1) # Sleep for 1 second       