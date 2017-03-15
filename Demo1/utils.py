'''
Helping stuff for detecting a yellow sign

'''
import time
import cv2
import picamera
import numpy as np
import sys # for command line arguments
from transform import order_points, four_point_transform    # the imagesearch crap

YELLOW_BOUNDS = ([15, 100, 100], [30, 255, 255])

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


