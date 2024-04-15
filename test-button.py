import RPi.GPIO as GPIO
import time

LIMIT_SWITCH_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN)

counter = 0
while True:
    if GPIO.input(LIMIT_SWITCH_PIN) == GPIO.HIGH:
        print("activated.")
        counter += 1
        print("counter: ", counter)
    else:
        print("deactivated!")

    time.sleep(0.1)

