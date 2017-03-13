import time
import cv2
import picamera
#from PIL import Image, ImageTk
import Tkinter as tk

# given a greyscale image, use canny edge detection to get a clean image
# of whatever it is you're looking at
def get_canny(grey, hsv):
    grey = cv2.GaussianBlur(grey, (5, 5), 0)
    grey = get_color(grey, hsv, boundaries)
    canny = cv2.Canny(grey, 100, 350)
    return canny

# get the image, as an hsv, rgb, and greyscale
def get_image():
    filename = str(sys.argv[1])
    image = cv2.imread(filename, 1)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.imread(filename, 0)
    return image, grey, hsv 



# ask for file name
#filename = raw_input("Enter filename for image: ")
#filename = filename + ".jpg"
with picamera.PiCamera() as camera:
	# capture image
	camera.resolution = (1024, 768)
	#camera.start_preview()
	time.sleep(2) # warm up the camera
	while True:
        camera.capture(filename)
        img = cv2.imread(filename)
		cv2.imshow("canny", get_canny
	#camera.stop_preview()

	# display image
	#img = cv2.imread(filename)
	#cv2.imshow(filename, img)
	#cv2.waitKey(0)
