import time
import cv2
import picamera
import numpy as np
import sys # for command line arguments

# hsv tuple boundaries for the different colors
red = ([150, 120, 120], [180, 255, 255])
green = ([45, 60, 60], [70, 255, 255])

# get the countours of an image
def draw_contours(canny):
	(_, contours, _) = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
	for c in contours:
		epsilon = 0.1*cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, epsilon, True)
		cv2.drawContours(canny, approx, -1, (0, 255, 0), 3)
	display_image("canny", canny)
	
# make a resized image half the size
def get_half_image(img):
	return cv2.resize(img, None, fx=.5, fy=.5, interpolation = cv2.INTER_AREA)

# display the resized image
def display_image(title, image):
	cv2.imshow(title, image)
	cv2.waitKey(0)
	return

# get the image, as an hsv 
def get_image():
	filename = str(sys.argv[1])
	image = cv2.imread(filename, 1)
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	grey = cv2.imread(filename, 0)
	return image, grey, hsv 

# make image go upside-down
def get_upside_down(image):
	rows, cols = image.shape

	M = cv2.getRotationMatrix2D((cols/2, rows/2), 180, 1)
	return cv2.warpAffine(image, M, (cols, rows))

def get_morphs(image):
	kernel = np.ones((5, 5), np.uint8)
	dilation = cv2.dilate(image, kernel, iterations = 1)
	opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
	closing = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
	return [dilation, opening, closing] 


# check if an image has a color based on a color range
def do_color_stuff(image, hsv, color_bounds):
	(lower, upper) = color_bounds
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	mask = cv2.inRange(hsv, lower, upper)
	mask = get_morphs(mask)[1]	# get the closing morph
	output = cv2.bitwise_and(hsv, hsv, mask = mask)

	cv2.imshow("images", np.hstack([get_half_image(output), get_half_image(hsv)]))
	cv2.waitKey(0)
	return

## MAIN STUFF
image, grey, hsv = get_image()
display_image("canny", image)
#do_color_stuff(image, hsv, green)
draw_contours(grey)
