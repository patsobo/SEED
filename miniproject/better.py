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

# initialize LCD
try:
    lcd = LCD.Adafruit_CharLCDPlate()
except IOError:
    flag = 12

# hsv tuple boundaries for the different colors
red_bounds= [([0, 100, 100], [10, 255, 255]), ([170, 100, 100], [180, 255, 255])]
green_bounds = [([45, 100, 100], [75, 255, 255])]

# constants to write to arduino for each color and distance
MAX_DISTANCE = 100
RED = MAX_DISTANCE
GREEN = MAX_DISTANCE + 1 

# camera constants
#RESOLUTION = (1020, 768)
RESOLUTION = (640, 480)

# ultrasonic sensor setup
TRIG = 16
ECHO = 18
#GPIO.setmode(GPIO.BOARD)        #ultrasonic sensor setup
GPIO.setup(TRIG,GPIO.OUT) #trigger
GPIO.setup(ECHO,GPIO.IN)  #echo
GPIO.output(TRIG,False)   #initial settings

# for RPI version 1, use “bus = smbus.SMBus(0)”
bus = smbus.SMBus(1)
# This is the address we setup in the Arduino Program
address = 0x04



################ COMPUTER VISION ########################

# take a picture without any of the preview stuff
def take_picture_simple(filename):
    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.capture(filename)
        return cv2.imread(filename)

# take picture with preview
def take_picture(filename):
    with picamera.PiCamera() as camera:
        # capture image
        #camera.awb_mode = 'flash'
        camera.resolution = RESOLUTION
        camera.start_preview()
        time.sleep(2) # warm up the camera
        camera.capture(filename)
        camera.stop_preview()
        return cv2.imread(filename)

# get the image, as an rgb, greyscale, and hsv
def get_image():
    filename = "temp.jpg"
    take_picture_simple(filename)
    image = cv2.imread(filename, 1)


################ COMPUTER VISION ########################

# take a picture without any of the preview stuff
def take_picture_simple(filename):
    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.capture(filename)
        return cv2.imread(filename)

# take picture with preview
def take_picture(filename):
    with picamera.PiCamera() as camera:
        # capture image
        #camera.awb_mode = 'flash'
        camera.resolution = RESOLUTION
        camera.start_preview()
        time.sleep(2) # warm up the camera
        camera.capture(filename)
        camera.stop_preview()
        return cv2.imread(filename)

# get the image, as an rgb, greyscale, and hsv 
def get_image():
    filename = "temp.jpg"
    take_picture_simple(filename)
    image = cv2.imread(filename, 1)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.imread(filename, 0)
    return image, grey, hsv 

# does the best morph I could think of 
def get_morphs(image):
    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(image, kernel, iterations = 1)
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
    return [dilation, opening, closing] 

# given an image, masks that image based on some color
def get_color_mask(image, hsv, color_bounds):
    mask = np.zeros(hsv.shape)
    for bound in color_bounds:
        (lower, upper) = bound 
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        
        new_mask = cv2.inRange(hsv, lower, upper)
        cv2.bitwise_or(mask, new_mask, mask)
        #mask = mask | new_mask 
    mask = get_morphs(mask)[1]    # get the closing morph
    #output = cv2.bitwise_and(hsv, hsv, mask = mask)
    return mask

# returns a bool if the specified color is found in the image
def contains_color(image, hsv, color_string, color_bounds):
    mask = get_color_mask(image, hsv, color_bounds)
    # if a significant area contains the color,
    # then return true
    print color_string, np.sum(mask)
    if (np.sum(mask) > 800000):
        return True
    return False    


################ COMM FUNCTIONS ###########################
def writeNumber(value):
    # run even when dumb exception occurs
    try:
        bus.write_byte(address, value)
    except IOError:
        #subprocess.call(['i2cdetect', '-y', '1'])
        flag = 1     #optional flag to signal your code to resend or something
    
    # bus.write_byte_data(address, 0, value)
    return -1

def readNumber():
    number = bus.read_byte(address)
    # number = bus.read_byte_data(address, 1)
    return number


################## OTHER FUNCTIONS ######################################
def measure_distance():
    GPIO.output(TRIG,True) #set pin 31 to on
    time.sleep(0.00001) #delay
    GPIO.output(TRIG,False) #set pin 31 to off
    while GPIO.input(ECHO) == 0:
        StartTime = time.time() #constantly sets starting time to now
    while GPIO.input(ECHO) == 1:
        EndTime = time.time() #constantly sets ending time to now
    #calculation for pulse duration time
        
    DurationTime = EndTime - StartTime
    distance = DurationTime*17150 #changes time to distance in cm
    return distance

# checks to see if red_bounds or green_bounds light detected
def process_image(image, hsv, prev_result):
    result = prev_result # set previous result by default if no color is found
    if (contains_color(image, hsv, "GREEN", green_bounds)): 
        result = GREEN 
    elif(contains_color(image, hsv, "RED", red_bounds)):
        result = RED 
    return result



##################### MAIN CALL #######################
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
time.sleep(0.1)
#
#prev_result = RED
#filename = "temp.jpg"
## standard picture setup
#while (True): 
#    camera.capture(filename)
#    image = cv2.imread(filename)
#    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# 
#    # process whether you've seen green_bounds or red_bounds 
#    result = process_image(image, hsv, prev_result)
#    writeNumber(int(result))
#    prev_result = result
#    #time.sleep(.1)    
#
#    distance = measure_distance() 
#    if distance < MAX_DISTANCE: #if anything is found
#        writeNumber(int(distance))
#        # sleep one second
#        #time.sleep(.1)
#    #print "Sent: %d, %f" % (result, distance)
#    
#    # show the frame
#    cv2.imshow("Frame", image)
#    cv2.waitKey(0)
#

prev_result = RED
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # process whether you've seen green_bounds or red_bounds 
    result = process_image(image, hsv, prev_result)
    writeNumber(int(result))
    prev_result = result
    time.sleep(.1)    

    distance = measure_distance() 
    if distance < MAX_DISTANCE: #if anything is found
        writeNumber(int(distance))
        # sleep one second
        time.sleep(.1)
    #print "Sent: %d, %f" % (result, distance)

    # calculate the speed of the motor for displaying   
    speed = distance * .106
    try: 
        lcd.clear()
        lcd.message('Distance in cm: %d\nSpeed of motor in rad/s: %d' % (int(distance), int(speed)))
    except IOError:
        flag = 1     #optional flag to signal your code to resend or something



    # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1)
    
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    
