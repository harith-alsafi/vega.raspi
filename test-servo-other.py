#!/usr/bin/python3
import pigpio
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 
servo = 13

# more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth

pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)



pwm.set_PWM_frequency( servo, 50 )

def set_angle(angle):
    pulse_width = (angle / 180.0) * (2500 - 500) + 500
    pwm.set_servo_pulsewidth(servo, pulse_width)
    time.sleep(3)  # Adjust this delay as needed

set_angle(0)
set_angle(45)
set_angle(90)
set_angle(135)
set_angle(180)
set_angle(0)

# turning off servo
pwm.set_PWM_dutycycle( servo, 0 )
pwm.set_PWM_frequency( servo, 0 )
pwm.stop()