import time
import cv2
import picamera
import numpy as np
import sys # for command line arguments

# tuple for the color yellow, in hsv
boundaries = ([10, 100, 100], [40, 255, 255])

# make a resized image half the size
def get_half_image(img):
	return cv2.resize(img, None, fx=.5, fy=.5, interpolation = cv2.INTER_AREA)

# display the resized image
def display_image(title, image):
	cv2.imshow(title, image)
	cv2.waitKey(0)
	return

# get the image, as an hsv, rgb, and greyscale
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

# does a bunch of morphs on the image and is generally useless
def get_morphs(image):
	kernel = np.ones((5, 5), np.uint8)
	dilation = cv2.dilate(image, kernel, iterations = 1)
	opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
	closing = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
	return [dilation, opening, closing] 


# check if an image has a color based on a color range
def get_color(image, hsv, color_bounds):
	(lower, upper) = color_bounds
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	mask = cv2.inRange(hsv, lower, upper)
	output = cv2.bitwise_and(hsv, hsv, mask = mask)

	return output
#	cv2.imshow("images", np.hstack([image, output]))
#	cv2.waitKey(0)

# given a greyscale image, use canny edge detection to get a clean image
# of whatever it is you're looking at
def get_canny(grey):
	grey = cv2.GaussianBlur(grey, (5, 5), 0)
	canny = cv2.Canny(grey, 100, 350)
	return canny

# write the image to a jpeg file
def save_image(filename, image):
	cv2.imwrite(filename + ".jpg", image)
	print "Save complete."
	return

## MAIN STUFF


print("""
0. Normal image
1. Halve the image
2. Make the image go upside down
3. Morph the image like crazy
4. Canny edge detection
""")

selection = raw_input("Take your pick:  ")
selection = int(selection)

img, grey, hsv = get_image()
if selection == 0:
	display_image("Regular", img)
elif selection == 1:
	halved = get_half_image(grey)
	display_image("Half da size", halved)
elif selection == 2:
	updown = get_upside_down(grey)
	display_image("Upside down", updown)
elif selection == 3:
	morphs_list = get_morphs(grey)
	for morph in morphs_list:
		display_image("...", morph)
elif selection == 4:
	canny = get_canny(grey)
	save_image("canny", canny)
	display_image("Canny", canny)

