import time
import cv2
import picamera
import numpy as np
import sys # for command line arguments
from transform import order_points, four_point_transform    # the imagesearch crap

# hsv tuple boundaries for the different colors
red = ([150, 120, 120], [180, 255, 255])
green = ([45, 60, 60], [70, 255, 255])

# get the countours of an image
def draw_contours(canny, original):
    (_, contours, _) = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # grab the first whatever number of contours for detection
    num_contours = 1
    if (len(contours) >= 3):
        num_contours = 3
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:num_contours]

    # iterate through the contours and find the octagon
    for c in contours:
        approx = get_approx(c, 8)    # 8 edges b/c it's a stop sign
        if (is_sign(approx)):
            break

    crit_points = [approx[0][0], approx[1][0], approx[2][0], approx[3][0]]
    print approx[:4]
    original = four_point_transform(original, approx[:4]) 
    cv2.drawContours(original, [approx], -1, (0, 255, 0), 3)
    display_image("canny", original)

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
    while (len(approx) != num_edges):
        multiplier += 0.001 
        epsilon = multiplier*cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
    return approx
        
 
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
    mask = get_morphs(mask)[1]    # get the closing morph
    output = cv2.bitwise_and(hsv, hsv, mask = mask)

    cv2.imshow("images", np.hstack([get_half_image(output), get_half_image(hsv)]))
    cv2.waitKey(0)
    return

## MAIN STUFF
image, grey, hsv = get_image()
original = cv2.imread("images/Stop_warped.jpg", 1)
display_image("canny", grey)
#do_color_stuff(image, hsv, green)
draw_contours(grey, original)
