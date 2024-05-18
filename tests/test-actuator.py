import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM (Broadcom SOC channel)
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins for the actuator control signals
STEP_PIN = 5  # GPIO pin for the step control

# Set the GPIO pins as output
GPIO.setup(STEP_PIN, GPIO.OUT)

while True:
    GPIO.output(STEP_PIN, GPIO.HIGH)
    time.sleep(0.5)