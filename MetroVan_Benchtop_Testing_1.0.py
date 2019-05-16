# This code is being developed to test the MetroVancouver Benchtop device. May 15, 2019.
import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15
import board
import busio
import adafruit_bme280
import digitalio
import adafruit_max31855

pinValve1 = 17
pinValve2 = 27

pinValve4 = 22
pinValve5 = 5
pinValve6 = 19
pinHeater = 26
pinLA = 4

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

def read_from_BME280_SPI():
   ## bme2 corresponds to the BME sensor communicating over the SPI network
   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) 
   cs = digitalio.DigitalInOut(board.D5)
   bme2 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)
   ## Read from second BME sensor (SPI)
   print("Pressure from second sensor: %0.1f hPa" % bme2.pressure)
   print("Temperature from second sensor: %0.1f C" % bme2.temperature)
   print("Humidity from second sensor: %0.1f %%" % bme2.humidity)
   print("Altitude from second sensor: %0.1f m" % bme2.altitude)

def read_from_BME280_I2C():
   ## bme280 corresponds to the BME sensor communicating over the I2C network
   i2c = busio.I2C(board.SCL, board.SDA)
   bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
   ## Read from first BME sensor (I2C)
   print("\nTemperature: %0.1f C" % bme280.temperature)
   print("Humidity: %0.1f %%" % bme280.humidity)
   print("Pressure: %0.1f hPa" % bme280.pressure)

def read_from_MAX31855():
   #Max31855
   max31855 = adafruit_max31855.MAX31855(spi, cs)
   tempC = max31855.temperature
   tempF = tempC*9/5 + 32
   print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f C" %tempC)
   print("Temperature from MAX31855 Thermocouple Amplifier: %0.1f F" %tempF)

def do_function(num):
   if num == '1':
       print("Valve 1")
       GPIO.output(pinValve1,GPIO.HIGH)
       time.sleep (0.5)
       GPIO.output(pinValve1,GPIO.LOW)
   elif num == '2':
       print("Reading from BME280 (SPI)")
       read_from_BME280_SPI()
   elif num == '3':
       print("Reading from BME280 (I2C)")
       read_from_BME280_I2C()
   elif num == '4':
       print("Reading from MAX31855")
       read_from_MAX31855()
   elif num == '5':
       print("Valve 5")
       GPIO.output(pinValve5,GPIO.HIGH)
       time.sleep (0.5)
       GPIO.output(pinValve5,GPIO.LOW)
   elif num == '6':
       print("Valve 6")
       GPIO.output(pinValve6,GPIO.HIGH)
       time.sleep (0.5)
       GPIO.output(pinValve6,GPIO.LOW)
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
   A = input("0 -> Heater:  1 -> Valve1:  2 -> BME280_SPI:  3 -> BME280_I2C:  4 -> MAX31855:  5 -> Valve5:  7 -> LA In:  8 -> LA Out:  9 -> MOS_Sensor:")
   if A == 'x':
       break
   else:
       do_function(A)

GPIO.cleanup()
