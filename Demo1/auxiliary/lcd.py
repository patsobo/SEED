# -*- coding: utf-8 -*-

import subprocess
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import smbus
import time
import RPi.GPIO as GPIO
import numpy as np
import Adafruit_CharLCD as LCD

GPIO.setmode(GPIO.BCM)
# initialize LCD
flag = -1
while (flag == -1):
    try:
        print "Initializing LCD..."
        lcd = LCD.Adafruit_CharLCDPlate()
        flag = 0
    except IOError:
        flag = -1
print "Found LCD"
   
while (True): 
    try:
        lcd.clear()
        time.sleep(1)
        lcd.message("PATRICK")
        #lcd.message('Dist cm:%d\nSpd rads:%d' % (int(distance), int(speed)))
        time.sleep(1)
    except IOError:
        flag = 123

    # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1)
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
