import time
import cv2
import picamera
import numpy as np
#from PIL import Image, ImageTk

# tuple for the color yellow, in hsv
boundaries = ([20, 100, 100], [30, 255, 255])


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
    grey = get_color(grey, hsv, boundaries)
    canny = cv2.Canny(grey, 100, 350)
    return canny

# get the image, as an hsv, rgb, and greyscale
def get_image(filename):
    image = cv2.imread(filename, 1)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.imread(filename, 0)
    return image, grey, hsv 


# ask for file name
#filename = raw_input("Enter filename for image: ")
#filename = filename + ".jpg"
filename = "temp.jpg"
with picamera.PiCamera() as camera:
    # capture image
    camera.resolution = (1024, 768)
    #camera.start_preview()
    time.sleep(2) # warm up the camera
    while True:
        camera.capture(filename)
        img,grey,hsv = get_image(filename)
        cv2.imshow("canny", get_canny(grey, hsv))
        cv2.waitKey(0)
    #camera.stop_preview()

    # display image
    #img = cv2.imread(filename)
    #cv2.imshow(filename, img)
    #cv2.waitKey(0)
