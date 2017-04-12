'''
Helping stuff for detecting a yellow sign

'''
import time
import subprocess
import cv2
import picamera
import numpy as np
import smbus
import RPi.GPIO as GPIO
import sys # for command line arguments
from transform import order_points, four_point_transform    # the imagesearch crap

YELLOW_BOUNDS = ([15, 100, 100], [30, 255, 255])

GPIO.setmode(GPIO.BCM)

# ultrasonic sensor setup
TRIG = 23 
ECHO = 24
GPIO.setup(TRIG,GPIO.OUT) #trigger
GPIO.setup(ECHO,GPIO.IN)  #echo
GPIO.output(TRIG,False)   #initial settings

bus = smbus.SMBus(1)
address = 0x04

# make image go upside-down
def get_upside_down(image):
    rows, cols = image.shape[0], image.shape[1]

    M = cv2.getRotationMatrix2D((cols/2, rows/2), 180, 1)
    return cv2.warpAffine(image, M, (cols, rows))


# display the resized image
def display_image(title, image):
    cv2.imshow(title, image)
    #time.sleep(1)
    cv2.waitKey(0)
    return

# draw contours
def draw_contours(original, approx):
    cv2.drawContours(original, [approx], -1, (0, 255, 0), 3)
    
    # draw dots on image
    #for point in np.squeeze(approx[:4]):
    #    original = cv2.circle(original, (int(point[0]), int(point[1])), 7, (0, 255, 0), -1)
    display_image("contour", original)
    return


# get all the detected contours of the image
def get_contours(canny):
    (_, contours, _) = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # grab the first whatever number of contours for detection
    num_contours = 1
    if (len(contours) >= 3):
        num_contours = 3
    return sorted(contours, key = cv2.contourArea, reverse = True)[:1]

# if the length of all the edges is ~ equal, then it's a sign 
def is_sign(points):
    size = len(points)
    distances = []
    # apologies for not being pythonic
    for i in range(size):
        distance = 100000
        # technically this checks all but the last points, but w/e
        for j in range(i + 1, size):
            if (get_distance(points[i][0], points[j][0]) < distance):
                distance = get_distance(points[i][0], points[j][0])
        if (distance != 100000):
            distances.append(distance)
  
    if (len(distances) <= 0):
        return False
 
    distances = sorted(distances)
    # now check for ~ equal distances
    # here it just checks if the last distance is about equal to all
    # the others
    largest = distances[-1]
    for i in range(len(distances) - 1):
        if (abs(distances[i] - largest) > 2*distances[i]):
            return False            
    return True 

# standard pythagorean theorem function
def get_distance(point1, point2):
    diff1 = abs(point2[0] - point1[0])
    diff2 = abs(point2[1] - point1[1])

    return np.sqrt(np.power(diff1, 2) + np.power(diff2, 2))
 
# given number of vertices, get the approx shape thing
# as a note, decrementing the multiplier seems to work better
def get_approx(contour, num_edges):
    multiplier = 0
    epsilon = multiplier*cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    while (len(approx) != num_edges and multiplier < 2):
        multiplier += 0.001 
        epsilon = multiplier*cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
    return approx
 

# check if an image has a color based on a color range
def get_color(image, hsv, color_bounds):
    (lower, upper) = color_bounds
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")

    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(hsv, hsv, mask = mask)

    return output

# given a greyscale image, use canny edge detection to get a clean image
# of whatever it is you're looking at
def get_canny(grey, hsv):
    grey = cv2.GaussianBlur(grey, (5, 5), 0)
    grey = get_color(grey, hsv, YELLOW_BOUNDS)
    canny = cv2.Canny(grey, 100, 350)
    return canny

################ COMM FUNCTIONS ###########################
def writeNumber(value):
    # run even when dumb exception occurs
    try:
        print "Sending", value
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


################## ULTRASONIC FUNCTIONS ######################################
def measure_distance():
    GPIO.output(TRIG,True) #set pin 31 to on
    time.sleep(0.00001) #delay
    GPIO.output(TRIG,False) #set pin 31 to off
    StartTime = time.time()
    while GPIO.input(ECHO) == 0:
        StartTime = time.time() #constantly sets starting time to now
    EndTime = time.time()
    while GPIO.input(ECHO) == 1:
        EndTime = time.time() #constantly sets ending time to now
    #calculation for pulse duration time
        
    DurationTime = EndTime - StartTime
    distance = DurationTime*17150 #changes time to distance in cm
    return distance

# jankier, but perhaps working function for distance
def get_distance():
    # begin doing something
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    time.sleep(.00001)

    count = 0
    data = []
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        data.append(GPIO.input(ECHO))
        pulse_start = time.time()
        count += 1
        if count > 2000:
            break
#        if GPIO.input(ECHO) == 1:
#            pulse_end = time.time()
#            break
#    time.sleep(.00001)
#    print "count:", count
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    data = []
    for i in range(100):
        data.append(GPIO.input(ECHO))
    #print data

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    #distance = round(distance, 2)
    return distance

