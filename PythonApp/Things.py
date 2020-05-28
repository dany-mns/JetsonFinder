#!/usr/bin/env python

import Jetson.GPIO as GPIO
import time


# This class is used to control a DC motor.
class Motor:
    def __init__(self, EN, IN1, IN2):
        self.speed = EN
        self.forward = IN1
        self.backward = IN2
        self.pwm = None

        # pins setup
        GPIO.setup(self.speed, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.forward, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.backward, GPIO.OUT, initial=GPIO.LOW)

        # pwm setup
        self.pwm = GPIO.PWM(self.speed, 50) # frequency of pwm signal: 50Hz
        self.pwm.start(0)

    def goForward(self):
        GPIO.output(self.forward, GPIO.HIGH)
        GPIO.output(self.backward, GPIO.LOW)

    def goBackward(self):
        GPIO.output(self.forward, GPIO.LOW)
        GPIO.output(self.backward, GPIO.HIGH)

    def stop(self):
        GPIO.output(self.forward, GPIO.LOW)
        GPIO.output(self.backward, GPIO.LOW)

    def setSpeed(self, value):
        # value must be between 0 and 100
        # 0->min speed | 100 -> max speed
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        self.pwm.ChangeDutyCycle(value)

    def __del__(self):
        # cleanup and leave pins in the safe state
        self.stop()
        self.pwm.stop()
        GPIO.cleanup([self.speed, self.forward, self.backward])


# This class is used to control a HC-SR04 ultrasonic sensor
class DistanceSensor:
    def __init__(self, TRIGGER, ECHO):
        self.trig = TRIGGER
        self.echo = ECHO

    # This function returns distance in cm or -1 value if the measurement failed.
    # Distance measurement using a ultrasonic sensor is a time-sensitive work.
    # So, because here runs Ubuntu OS, I think it depends by process scheduling.
    # Sometimes it work with an error of max 2 cm, sometimes it doesn't.
    # Doesn't work for distance < 4 cm (echo pulse is too fast ~230us).
    def getDistance(self):
        # pins setup
        GPIO.setup(self.trig, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.echo, GPIO.IN)

        # set Trigger to HIGH for 10 us
        GPIO.output(self.trig, GPIO.HIGH)
        time.sleep(0.00001) # 10 us
        GPIO.output(self.trig, GPIO.LOW)

        # start counting time at Echo rising edge
        GPIO.wait_for_edge(self.echo, GPIO.RISING, timeout=100) # 100 ms
        startTime = time.time()

        # stop counting time at Echo falling edge
        GPIO.wait_for_edge(self.echo, GPIO.FALLING, timeout=100) # 100 ms
        elapsedTime = time.time() - startTime   # in seconds

        distance = -1
        # check if the measurement succeeded
        if elapsedTime < 0.1:
            # get the distance in cm using sonic speed (aprox. 34300 cm/s)
            distance = (elapsedTime * 34300) / 2

        GPIO.cleanup([self.trig, self.echo])
        return distance

    def __del__(self):
        GPIO.cleanup([self.trig, self.echo])
