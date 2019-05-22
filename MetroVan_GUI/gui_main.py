#Last edit: 22/05/2019
# -----> System Imports <-----
import os
import sys
import datetime
import time
# -----> Tkinter Imports <------
import tkinter as tk
from tkinter import ttk
# -----> Matplotlib Imports <------
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
# -----> Auxiliary Imports <------
from gui_widgets import *
# -----> RPi Imports <------
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

#####################          GUI           #######################
projectName = 'MetroVan Project'
class MetroVanGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs) #Passes all aguments to the parent class.

        self.title(projectName + ' GUI') #Title of the master window.
        self.geometry('640x480') #Initial size of the master window.
        # self.resizable(0,0) #The allowance for the master window to be adjusted by.

        canvas = tk.Frame(self) #Creates the area for which pages will be displayed.
        canvas.place(relx=0, rely=0, relheight=0.95, relwidth=1) #Defines the area which each page will be displayed.
        canvas.grid_rowconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.
        canvas.grid_columnconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.

        self.tabBar = tk.Frame(self) #Creates the area for which control buttons will be placed.
        self.tabBar.place(relx=0, rely=0.95, relheight=0.05, relwidth=1) #Defines the area for which control buttons will be placed.

        self.frames = {} #Dictonary to store each frame after creation.

        for f in (HomePage, DataPage, ManualControlPage): #For pages to be added, do the following:
            frame = f(canvas,self) #Creates a frame of the above classes.
            self.frames[f] = frame #Add the created frame to the 'frames' dictionary.
            frame.grid(row=0, column=0, sticky="nsew") #Overlaps the frame in the same grid space.
        self.show_frame(HomePage) #Sets the default page.
        print('System ready.')

    def show_frame(self, cont): #Control buttons will run this command for their corresponding pages.
        frame = self.frames[cont]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Home', command=lambda: controller.show_frame(HomePage))
        control_btn.pack(side='left', expand= True, fill = 'both')

        title = tk.Label(self, text=projectName, font=14, relief='solid')
        title.place(relx=0.2,rely=0.3,relwidth=0.6,relheight=0.15)

        intro = '''This interface allows user to actuate 10 different functions from the control panel.
        Functions include the control over the heater, 3 valves, bidirectional control of a linear actuator,
        and 4 sensors. These sensors include two BME280 Temp, Press and Humidity sensors, an ADC1115, and a
        MAX31855 Thermocouple amplifier, wired to the SPI network.'''

        introduction = tk.Label(self, text=intro, anchor='n')
        introduction.place(relx=0.1,rely=0.55,relheight=0.5,relwidth=0.8)

class DataPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Data', command=lambda: controller.show_frame(DataPage))
        control_btn.pack(side='left', expand= True, fill = 'both')

        self.graph = LiveGraph(self)
        self.graph.place(relx=0,rely=0,relheight=1,relwidth=1)

class ManualControlPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Manual Controls', command=lambda: controller.show_frame(ManualControlPage))
        control_btn.pack(side='left', expand= True, fill = 'both')

        controlFrame = tk.Frame(self)
        controlFrame.place(relx=0,rely=0,relheight=1,relwidth=0.6)

        motionFrame = tk.LabelFrame(controlFrame, text="System Controls")
        motionFrame.place(relx=0,rely=0,relheight=(1/3),relwidth=1)
        valveFrame = tk.LabelFrame(controlFrame, text="Valve Controls")
        valveFrame.place(relx=0,rely=(1/3),relheight=(1/4),relwidth=1)
        readFrame = tk.LabelFrame(controlFrame, text="Read Data")
        readFrame.place(relx=0,rely=(7/12),relheight=(1/3),relwidth=1)

        terminal = tk.Frame(self)
        CoreGUI(terminal)
        terminal.place(relx=0.6,rely=0,relheight=1,relwidth=0.4)


        buttonWidth = 0.35
        motionButtons = tk.Frame(motionFrame)
        motionButtons.place(relx=0,rely=0,relwidth=buttonWidth,relheight=1)
        valveButtons = tk.Frame(valveFrame)
        valveButtons.place(relx=0,rely=0,relwidth=buttonWidth,relheight=1)
        readButtons = tk.Frame(readFrame)
        readButtons.place(relx=0,rely=0,relwidth=buttonWidth,relheight=1)

        motionLabels = tk.Frame(motionFrame)
        motionLabels.place(relx=buttonWidth,rely=0,relwidth=(1-buttonWidth),relheight=1)
        valveLabels = tk.Frame(valveFrame)
        valveLabels.place(relx=buttonWidth,rely=0,relwidth=(1-buttonWidth),relheight=1)
        readLabels = tk.Frame(readFrame)
        readLabels.place(relx=buttonWidth,rely=0,relwidth=(1-buttonWidth),relheight=1)


        motionbtn_1 = tk.Button(motionButtons, text='Motor In', command=lambda:move_motor_out())
        motionbtn_1.pack(expand=True, fill='both', padx=2, pady=2)
        motionlbl_1 = tk.Label(motionLabels, text='[DESCRIPTION]', anchor='w')
        motionlbl_1.pack(expand=True, fill='both', padx=2, pady=2)

        motionbtn_2 = tk.Button(motionButtons, text='Motor Out', command=lambda:move_motor_in())
        motionbtn_2.pack(expand=True, fill='both', padx=2, pady=2)
        motionlbl_2 = tk.Label(motionLabels, text='[DESCRIPTION]', anchor='w')
        motionlbl_2.pack(expand=True, fill='both', padx=2, pady=2)

        motionbtn_3 = tk.Button(motionButtons, text='Actuate Stepper Motor', command=lambda:actuate_stepper_motor())
        motionbtn_3.pack(expand=True, fill='both', padx=2, pady=2)
        motionlbl_3 = tk.Label(motionLabels, text='[DESCRIPTION]', anchor='w')
        motionlbl_3.pack(expand=True, fill='both', padx=2, pady=2)

        motionbtn_4 = tk.Button(motionButtons, text='Heater', command=lambda:control_heater())
        motionbtn_4.pack(expand=True, fill='both', padx=2, pady=2)
        motionlbl_4 = tk.Label(motionLabels, text='[DESCRIPTION]', anchor='w')
        motionlbl_4.pack(expand=True, fill='both', padx=2, pady=2)


        valvebtn_1 = tk.Button(valveButtons, text='Valve 1', command=lambda:control_valve_1())
        valvebtn_1.pack(expand=True, fill='both', padx=2, pady=2)
        valvelbl_1 = tk.Label(valveLabels, text='[DESCRIPTION]', anchor='w')
        valvelbl_1.pack(expand=True, fill='both', padx=2, pady=2)

        valvebtn_2 = tk.Button(valveButtons, text='Valve 5', command=lambda:control_valve_5())
        valvebtn_2.pack(expand=True, fill='both', padx=2, pady=2)
        valvelbl_2 = tk.Label(valveLabels, text='[DESCRIPTION]', anchor='w')
        valvelbl_2.pack(expand=True, fill='both', padx=2, pady=2)

        valvebtn_3 = tk.Button(valveButtons, text='none', command='none')
        valvebtn_3.pack(expand=True, fill='both', padx=2, pady=2)
        valvelbl_3 = tk.Label(valveLabels, text='[DESCRIPTION]', anchor='w')
        valvelbl_3.pack(expand=True, fill='both', padx=2, pady=2)


        readbtn_1 = tk.Button(readButtons, text='BME280 I2C', command=lambda:read_from_BME280_I2C())
        readbtn_1.pack(expand=True, fill='both', padx=2, pady=2)
        readlbl_1 = tk.Label(readLabels, text='[DESCRIPTION]', anchor='w')
        readlbl_1.pack(expand=True, fill='both', padx=2, pady=2)

        readbtn_2 = tk.Button(readButtons, text='BME280 I2C (2)', command=lambda:read_from_BME280_I2C_2())
        readbtn_2.pack(expand=True, fill='both', padx=2, pady=2)
        readlbl_2 = tk.Label(readLabels, text='[DESCRIPTION]', anchor='w')
        readlbl_2.pack(expand=True, fill='both', padx=2, pady=2)

        readbtn_3 = tk.Button(readButtons, text='MAX31855', command=lambda:read_from_MAX31855())
        readbtn_3.pack(expand=True, fill='both', padx=2, pady=2)
        readlbl_3 = tk.Label(readLabels, text='[DESCRIPTION]', anchor='w')
        readlbl_3.pack(expand=True, fill='both', padx=2, pady=2)

        readbtn_4 = tk.Button(readButtons, text='MOS', command=lambda:read_from_MOS())
        readbtn_4.pack(expand=True, fill='both', padx=2, pady=2)
        readlbl_4 = tk.Label(readLabels, text='[DESCRIPTION]', anchor='w')
        readlbl_4.pack(expand=True, fill='both', padx=2, pady=2)

def main(self):
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

def control_heater():
    print("Heater on")
    GPIO.output(pinHeater,GPIO.HIGH)
    time.sleep (2)
    GPIO.output(pinHeater,GPIO.LOW)

def control_valve_1():
   print("Valve 1")
   GPIO.output(pinValve1,GPIO.HIGH)
   time.sleep (0.5)
   GPIO.output(pinValve1,GPIO.LOW)

def control_valve_5():
   print("Valve 5")
   GPIO.output(pinValve6,GPIO.HIGH)
   time.sleep (0.5)
   GPIO.output(pinValve6,GPIO.LOW)

try:
    main()
    app = MetroVanGUI()
    app.mainloop()
except keyboardinterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
