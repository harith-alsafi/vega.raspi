# Raspberry Pi + MG90S Servo PWM Control Python Code
#
#
import RPi.GPIO as GPIO
import time

# setup the GPIO pin for the servo
servo_pin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin,GPIO.OUT)

# setup PWM process
pwm = GPIO.PWM(servo_pin,50) # 50 Hz (20 ms PWM period)

zero_degree = 2.0
ninety_degree = 7.0
oneeighty_degree = 12.0
pwm.start(0) # start PWM by rotating to 90 degrees

def SetAngle(angle):
	duty = angle / 18 + 2
	GPIO.output(servo_pin, True)
	pwm.ChangeDutyCycle(duty)
	time.sleep(3)
	pwm.ChangeDutyCycle(0)
	GPIO.output(servo_pin, False)

SetAngle(120)
SetAngle(0)
SetAngle(120)
SetAngle(0)

# for ii in range(0,3):
#     pwm.ChangeDutyCycle(oneeighty_degree) # rotate to 0 degrees
#     time.sleep(0.5)
#     pwm.ChangeDutyCycle(ninety_degree) # rotate to 180 degrees
#     time.sleep(0.5)
#     pwm.ChangeDutyCycle(ninety_degree) # rotate to 90 degrees
#     time.sleep(0.5)

# pwm.ChangeDutyCycle(0) # this prevents jitter
pwm.stop() # stops the pwm on 13
GPIO.cleanup() # good practice when finished using a pin