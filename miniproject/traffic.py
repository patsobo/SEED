'''
Loops infinitely taking pictures, detect if there's a green or red
light ahead.

'''
import sys
import time
import cv2
import picamera
import numpy as np


# hsv tuple boundaries for the different colors
red = ([0, 100, 100], [10, 255, 255])
green = ([45, 100, 100], [75, 255, 255])

# take a picture without any of the preview stuff
def take_picture_simple(filename):
	with picamera.PiCamera() as camera:
		camera.resolution = (1024, 768)
		camera.capture(filename)
		return cv2.imread(filename)

# take picture with preview
def take_picture(filename):
	with picamera.PiCamera() as camera:
		# capture image
		#camera.awb_mode = 'flash'
		camera.resolution = (1024, 768)
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
	(lower, upper) = color_bounds
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	mask = cv2.inRange(hsv, lower, upper)
	mask = get_morphs(mask)[1]	# get the closing morph
	#output = cv2.bitwise_and(hsv, hsv, mask = mask)
	return mask

# returns a bool if the specified color is found in the image
def contains_color(image, hsv, color_bounds):
	mask = get_color_mask(image, hsv, color_bounds)
	# if a significant area contains the color,
	# then return true
	print np.sum(mask)
	if (np.sum(mask) > 2000000):
		return True
	return False	

# TODO: send result to arduino
def send_result(result):
	print result

result = "None"
while (True):
	image, grey, hsv = get_image()
	if (contains_color(image, hsv, green)):
		result =  "Green"
	elif(contains_color(image, hsv, red)):
		result =  "Red"
	else:
		result = "None"
	send_result(result)
