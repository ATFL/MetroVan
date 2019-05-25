import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15
import board
import busio
import adafruit_bme280
import adafruit_bme280_76
import digitalio
import adafruit_max31855

class LinearActuator:
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(8.1)
        time.sleep(0.5)
        self.state = 'retracted'

    def extend(self):
        print('Extending linear actuator.')
        self.pwm.ChangeDutyCycle(5.8)
        time.sleep(0.5)
        self.state = 'extended'

    def retract(self):
        print('Retracting linear actuator.')
        self.pwm.ChangeDutyCycle(8.1)
        time.sleep(0.5)
        self.state = 'retracted'

class StepperMotor:
    def __init__(self, DIRpin, STEPpin, MODE, **kwargs):
        #MODE is Microstep Resolution GPIO Pins, Example: MODE = (15, 18, 23)
        self.DIRpin = DIRpin
        self.STEPpin = STEPpin
        self.MODE = MODE
        GPIO.setup(self.DIRpin, GPIO.OUT)
        GPIO.setup(self.STEPpin, GPIO.OUT)

        self.step_per_rev = 3200 # the number of steps to complete one revolution
        self.delay = .0208/16 # the length of time between cycling current through coils

        if resolution in kwargs:
            self.res = resolution
        else:
            self.res = '1/16'

        GPIO.setup(self.MODE, GPIO.OUT)
        self.RESOLUTION = {'Full': (0, 0, 0),
                      'Half': (1, 0, 0),
                      '1/4': (0, 1, 0),
                      '1/8': (1, 1, 0),
                      '1/16': (0, 0, 1),
                      '1/32': (1, 0, 1)}
        GPIO.output(self.MODE, self.RESOLUTION[self.res])

    def rotateCW(self, rev):
        print('Rotating stepper motor clockwise by {} revolutions.'.format(rev))
        CW = 1
        GPIO.output(self.DIRpin, CW)
        step_count = rev * self.step_per_rev
        for i in range(int(step_count)):
            GPIO.output(self.STEPpin, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.STEPpin, GPIO.LOW)
            time.sleep(self.delay)

    def rotateCCW(self, rev):
        print('Rotating stepper motor counter-clockwise by {} revolutions.'.format(rev))
        CCW = 0
        GPIO.output(self.DIRpin, CCW)
        step_count = rev * self.step_per_rev
        for i in range(int(step_count)):
            GPIO.output(self.STEPpin, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.STEPpin, GPIO.LOW)
            time.sleep(self.delay)

class Valve:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False

    def switch(self):
        if self.state == False:
            self.enable()
        elif self.state == True:
            self.disable()

    def enable(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        print('Valve enabled.')

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print('Valve disabled.')

class Heater:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False

    def switch(self):
        if self.state == False:
            self.enable()
        elif self.state == True:
            self.disable()

    def enable(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        print('Heater enabled.')

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print('Heater disabled.')

class BME280:
    def __init__(self, bme280):
        self.bme280 = bme280

    def temperature(self):
        return self.bme280.temperature

    def humidity(self):
        return self.bme280.humidity

    def pressure(self):
        return self.bme280.pressure

    def print(self):
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)

class MAX31855:
    def __init__(self):
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs = digitalio.DigitalInOut(board.D21)
        self.max31855 = adafruit_max31855.MAX31855(spi, cs)
        self.tempC = max31855.temperature
        self.tempF = tempC*9/5 + 32

    def _update(self):
        self.tempC = self.max31855.temperature
        self.tempF = tempC*9/5 + 32

    def temperature_C(self):
        self._update()
        return self.tempC

    def temperature_F(self):
        self._update()
        return self.tempF

    def print(self):
        self._update()
        print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f C" %self.tempC)
        print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f F" %self.tempF)

class MOS:
    def __init__(self, adc, channel):
        # Choose a gain of 1 for reading voltages from 0 to 4.09V.
        # Or pick a different gain to change the range of voltages that are read:
        #  - 2/3 = +/-6.144V
        #  -   1 = +/-4.096V
        #  -   2 = +/-2.048V
        #  -   4 = +/-1.024V
        #  -   8 = +/-0.512V
        #  -  16 = +/-0.256V
        # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144

    def read(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        return self.conversion_value
