# This code is being developed to test the MetroVancouver Benchtop device. May 15, 2019.
# Code allows user to actuate 10 different functions from the command terminal.
# Functions include heater, 3 valves, bidirectional control of a linear actuator,
# and 4 sensors. These sensors include two BME280 Temp, Press and Humidity sensors,
# both wired to the I2C network, an ADC1115 (also on I2C network), and a 
# MAX31855 Thermocouple amplifier, wired to the SPI network. In order to make
# both BME280 sensors operate on the same I2C network, a separate library
# was needed to specify a new address (0x76), created by jumping the SDO pin
# of the second BME280 sensor to ground. The edited library is called 
# adafruit_bme280_76. The standard library is adafruit_bme280, which looks 
# for the sensor at the default address of 0x77.
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

pinValve1 = 17
pinValve2 = 27

pinValve4 = 22
pinValve5 = 5
pinValve6 = 19
pinHeater = 26
pinLA = 4

#Stepper Motor Pins
DIR = 25   # Direction GPIO Pin
STEP = 24  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 400   # Steps per Revolution (360 / 7.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pinValve1,GPIO.OUT)
GPIO.setup(pinValve2,GPIO.OUT)
GPIO.setup(pinValve4, GPIO.OUT)
GPIO.setup(pinValve5, GPIO.OUT)
GPIO.setup(pinValve6, GPIO.OUT)
GPIO.setup(pinHeater, GPIO.OUT) 
GPIO.setup(pinLA, GPIO.OUT)
GPIO.setup(pinValve1,GPIO.LOW)
GPIO.setup(pinValve2,GPIO.LOW)
GPIO.setup(pinValve4, GPIO.LOW)
GPIO.setup(pinValve5, GPIO.LOW)
GPIO.setup(pinValve6, GPIO.LOW)
GPIO.setup(pinHeater, GPIO.LOW)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(pinLA,GPIO.LOW)
pwm = GPIO.PWM(pinLA, 50) # Set pin 16 to be pulse width modulated at a frequency of 50 Hz
pwm.start(7)
A = 0

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115(0x48)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 2 / 3

#######################################################################
######################### Stepper Motor ##############################
MODE = (15, 18, 23)   # Microstep Resolution GPIO Pins
GPIO.setup(MODE, GPIO.OUT)
RESOLUTION = {'Full': (0, 0, 0),
              'Half': (1, 0, 0),
              '1/4': (0, 1, 0),
              '1/8': (1, 1, 0),
              '1/16': (0, 0, 1),
              '1/32': (1, 0, 1)}
GPIO.output(MODE, RESOLUTION['1/16'])


########################## User Defined Functions ############################
def move_motor_out():
   print("Moving Motor Out")
   pwm.ChangeDutyCycle(5.8) #values based on testing with new setup with isaac april 27th Max out

def move_motor_in():
   print("Moving Motor in")
   pwm.ChangeDutyCycle(8.1) #values based on testing with new setup with isaac april 27th max in

def read_from_MOS():
   #Read from ADC
   chan = 1
   conversion_value = (adc.read_adc(chan,gain=GAIN)/pow(2, 15))*6.144
   print(conversion_value)
   time.sleep(0.5)

def read_from_BME280_I2C_2():
   ## bme280 corresponds to the BME sensor communicating over the I2C network
   i2c = busio.I2C(board.SCL, board.SDA)
   bme280 = adafruit_bme280_76.Adafruit_BME280_I2C(i2c)
   ## Read from second BME280 sensor (I2C_2)
#   print(i2c)
   print("\nTemperature: %0.1f C" % bme280.temperature)
   print("Humidity: %0.1f %%" % bme280.humidity)
   print("Pressure: %0.1f hPa" % bme280.pressure)
#   ## bme2 corresponds to the BME sensor communicating over the SPI network
#   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) 
#   cs = digitalio.DigitalInOut(board.D14)
#   bme2 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)
#   ## Read from second BME sensor (SPI)
#   print("Pressure from second sensor: %0.1f hPa" % bme2.pressure)
#   print("Temperature from second sensor: %0.1f C" % bme2.temperature)
#   print("Humidity from second sensor: %0.1f %%" % bme2.humidity)
#   print("Altitude from second sensor: %0.1f m" % bme2.altitude)

def read_from_BME280_I2C():
   ## bme280 corresponds to the BME sensor communicating over the I2C network
   i2c = busio.I2C(board.SCL, board.SDA)
   bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
   ## Read from first BME280 sensor (I2C)
#   print(i2c)
   print("\nTemperature: %0.1f C" % bme280.temperature)
   print("Humidity: %0.1f %%" % bme280.humidity)
   print("Pressure: %0.1f hPa" % bme280.pressure)

def read_from_MAX31855():
   #Max31855
   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
   cs = digitalio.DigitalInOut(board.D21)
   max31855 = adafruit_max31855.MAX31855(spi, cs)
   tempC = max31855.temperature
   tempF = tempC*9/5 + 32
   print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f C" %tempC)
   print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f F" %tempF)
def actuate_stepper_motor():
   GPIO.output(DIR, CW)

   # the total number of steps travelled by stepper motor before reversing
   step_count = SPR*8

   # the length of time between cycling current through coils
   delay = .0208/16 

   for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(delay)

   time.sleep(.5)
   GPIO.output(DIR, CCW)
   for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(delay)


def do_function(num):
   if num == '1':
       print("Valve 1")
       GPIO.output(pinValve1,GPIO.HIGH)
       time.sleep (0.5)
       GPIO.output(pinValve1,GPIO.LOW)
   elif num == '2':
       print("Reading from BME280 (I2C_2)")
       read_from_BME280_I2C_2()
   elif num == '3':
       print("Reading from BME280 (I2C)")
       read_from_BME280_I2C()
   elif num == '4':
       print("Reading from MAX31855")
       read_from_MAX31855()
   elif num == '5':
       print("Valve 5")
       GPIO.output(pinValve6,GPIO.HIGH)
       time.sleep (0.5)
       GPIO.output(pinValve6,GPIO.LOW)
   elif num == '6':
       print("Stepper Motor")
       actuate_stepper_motor()
   elif num == '7':
       print("Linear Actuator In")
       move_motor_in()
   elif num == '8':
       print("Linear Actuator Out")
       move_motor_out()
   elif num == '9':
       print("Reading from MOS sensor")
       read_from_MOS()
   elif num == '0':
       print("Heater on")
       GPIO.output(pinHeater,GPIO.HIGH)
       time.sleep (2)
       GPIO.output(pinHeater,GPIO.LOW)
   else:
       print("invalid")

while True:
   A = input("0 -> Heater:  1 -> Valve1:  2 -> BME280_I2C_2:  3 -> BME280_I2C:  4 -> MAX31855:  5 -> Valve5: 6 -> Stepper Motor:  7 -> LA In:  8 -> LA Out:  9 -> MOS_Sensor:")
   if A == 'x':
       break
   else:
       do_function(A)

GPIO.cleanup()
