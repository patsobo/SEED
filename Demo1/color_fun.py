import time
import cv2
import picamera
import numpy as np
import sys # for command line arguments
from transform import order_points, four_point_transform    # the imagesearch crap

# hsv tuple boundaries for the different colors
red = ([150, 120, 120], [180, 255, 255])
green = ([45, 60, 60], [70, 255, 255])

def get_contours(canny):
    (_, contours, _) = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # grab the first whatever number of contours for detection
    num_contours = 1
    if (len(contours) >= 3):
        num_contours = 3
    return sorted(contours, key = cv2.contourArea, reverse = True)[:num_contours]

# get the countours of an image
def draw_contours(canny, original, template):
    contours = get_contours(canny)

    # iterate through the contours and find the octagon
    for c in contours:
        approx = get_approx(c, 4)    # 8 edges b/c it's a stop sign, 4 for other signs
        if (is_sign(approx)):
            break

    warped = four_point_transform(original, np.squeeze(approx[:4]))
    cv2.imwrite("warped.jpg", warped) 
    cv2.drawContours(original, [approx], -1, (0, 255, 0), 3)
    
    # draw dots on image
    for point in np.squeeze(approx[:4]):
        original = cv2.circle(original, (int(point[0]), int(point[1])), 7, (0, 255, 0), -1)

    # convert to black and white 
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    ret, warped = cv2.threshold(warped, 90, 255, cv2.THRESH_BINARY) 

    # compare against the template left turn image
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    ret, template = cv2.threshold(template, 90, 255, cv2.THRESH_BINARY)
    template = cv2.resize(template, (warped.shape[1], warped.shape[0])) # x and y lengths of your warped image (resize the template)
    total_pixels = warped.shape[0]*warped.shape[1]
    match_sum = 0
    for i in range(0, warped.shape[0] - 1):    
        for j in range(0, warped.shape[1] - 1):
            pixel = template[i][j]
            my_pixel = warped[i][j]
            if (pixel == my_pixel):
                match_sum += 1    
    print match_sum, total_pixels
    if (float(match_sum) / total_pixels >= 0.85):
        print "I found a left turn"
    else:
        print "I didn't find a left turn"
    display_image("canny", warped)

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
    while (len(approx) != num_edges and multiplier < 2):
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
#image, grey, hsv = get_image()
#original = cv2.imread("left_warped.jpg", 1)
#template = cv2.imread("images/Turn_Left.png", 1)
#display_image("canny", grey)
##do_color_stuff(image, hsv, green)
#draw_contours(grey, original, template)
