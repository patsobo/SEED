import time
import cv2
import picamera
from PIL import Image, ImageTk
import Tkinter as tk

# ask for file name
filename = raw_input("Enter filename for image: ")
filename = filename + ".jpg"

with picamera.PiCamera() as camera:
	# capture image
	camera.resolution = (1024, 768)
	camera.start_preview()
	time.sleep(2) # warm up the camera
	camera.capture(filename)
	camera.stop_preview()

	# display image
	img = cv2.imread(filename)
	cv2.imshow(filename, img)
	cv2.waitKey(0)
