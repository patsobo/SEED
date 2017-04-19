'''
A computer vision project to have a robot with a Pi camera attached
determine if it is looking at a set of pre-determined signs (Stop, Left, Right).
The sign template images are found in the images/ directory.
'''

from transform import * # helps with perspective warp
from utils import * # functions for getting the canny image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import math
import Adafruit_CharLCD as LCD

# initialize LCD
flag = -1
while (flag == -1):
    try:
        print "Initializing LCD..."
        lcd = LCD.Adafruit_CharLCDPlate()
        flag = 0
    except IOError:
        flag = -1
print "Found LCD."

# camera and template image constants
RESOLUTION = (1020, 768)
STOP_TEMPLATE = cv2.imread("images/Stop_template.jpg", 1)
STOP_TEMPLATE_2 = cv2.imread("images/Stop_template_2.jpg", 1)
LEFT_TEMPLATE = cv2.imread("images/Turn_Left.png", 1)
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)
SIGN_DIM = (1280, 962)

# returns what percentage of the warped image's pixels match the given
# template image
def matches_template(warped, template, matching=0.75):
    """
    Determines how closely a warped image from the real world
    matches a standard template image

    :params warped: the cv2 image taken from the real world
    :params template: the standardized template cv2 image to compare to

    :returns a decimal between 0 and 1 indicating the percentage of pixels matched
    """
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    ret, template = cv2.threshold(template, 90, 255, cv2.THRESH_BINARY)
    template = cv2.resize(template, None, fx=float(warped.shape[1])/template.shape[1], fy=float(warped.shape[0])/template.shape[0], interpolation=cv2.INTER_AREA) # x and y lengths of your warped image (resize the template)
    total_pixels = warped.shape[0]*warped.shape[1]
    if (total_pixels < 2*200):
        return False
    match_sum = 0
    for i in range(0, warped.shape[0]):    
        for j in range(0, warped.shape[1]):
            pixel = template[i][j]
            my_pixel = warped[i][j]
            if (pixel == my_pixel):
                match_sum += 1    
    #print "MATHC", float(match_sum) / total_pixels
    return (float(match_sum) / total_pixels >= matching)

def determine_sign(image, canny):
    """
    Calculates the sign seen by the Raspberry Pi camera.

    :params image: The actual raw image captured by the Pi camera.
    :params canny: The image with all the contours, created using cv2

    :returns a string representing the sign found, and the angle the sign is from the robot.
    """
    contours = get_contours(canny)

    #display_image("canny", canny)

    # iterate through contours and find the rectangles
    approx = []
    for c in contours:
        approx = get_approx(c, 4)    # 4 vertices for rect
    
    #draw_contours(image, approx)
    
    sign = "None"
    angle = 0
    points = []
    if (len(np.squeeze(approx)) >= 4):
        # flatten the image
        M, warped = four_point_transform(image, np.squeeze(approx[:4]))

        # convert to black and white 
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        ret, warped = cv2.threshold(warped, 90, 255, cv2.THRESH_BINARY) 

        AREA_CONST = 1
        # compare against the templates
        if (matches_template(warped, LEFT_TEMPLATE)):
            sign = "Left"
            AREA_CONST = 6.45
        elif (matches_template(warped, RIGHT_TEMPLATE)):
            sign = "Right"
            AREA_CONST = 6.45        
        elif (matches_template(warped, STOP_TEMPLATE, 0.95) or matches_template(warped, STOP_TEMPLATE_2, 0.95)):
            sign = "Stop"
            AREA_CONST = 9
            SIGN_DIM  = [100, 100]

        #display_image("canny", warped)
        #draw_contours(image, approx)

        # get area of sign in image
        area = cv2.contourArea(approx)

        # get center of sign in image
        approx = np.squeeze(approx)
        x_center = (approx[0][0] + approx[1][0] + approx[2][0] + approx[3][0]) / 4

        # find angle
        image_center = (RESOLUTION[0] / 2, RESOLUTION[1] / 2)
        difference = x_center - image_center[0]    # just need x-diff
        if (difference == 0):
            difference = 1
        distance = float(AREA_CONST)*(float(343)/abs(difference))*math.sqrt(area)

        # prevent division by 0
        if (distance == 0):
            distance = 1
        angle = math.degrees(math.atan(float(difference) / distance))

    return angle, sign

def draw_points(image, points):
    """
    Draws the points on the specified image.
    """
    # draw dots on image
    for point in np.squeeze(points):
        image = cv2.circle(image, (int(point[0]), int(point[1])), 7, (0, 255, 0), -1)
    display_image("points", image)

def scale_points(scale, points):
    """
    Applies the scale factor on all the points in the points array.
    """
    result = []
    for point in points:
        result.append((point[0] / scale[0], point[1] / scale[1]))
    return result

def cv_capture(camera, filename):
    # get the image
    camera.capture(filename)
    #filename = str(sys.argv[1])
    image = cv2.imread(filename)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect the sign type
    canny = get_canny(grey, hsv)
    angle, sign = determine_sign(image, canny)
    print sign, angle
    return sign, angle


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = RESOLUTION
camera.awb_mode = 'flash'
rawCapture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
time.sleep(0.1)
filename = "temp.jpg"

# loop to track how often to check for sign
CV_COUNT = 7
count = CV_COUNT 

# default values
sign = "None"
angle = 0

# main loop
while (True):
    if (count >= CV_COUNT):
        sign, angle = cv_capture(camera, filename)
        count = 0
    distance = measure_distance()
    print "DISTANCE", distance

    if sign != "None":
        if abs(angle) < 30 and abs(angle) > 4:
            writeNumber(int(angle) + 30)
            count = CV_COUNT    # re-check sign and angle immediately
            time.sleep(0.1)
        else:
            writeNumber(101)
            #time.sleep(0.1)
        if distance < 60:
            if sign == "Left":
                writeNumber(103)
            elif sign == "Right":
                writeNumber(104)
            elif sign == "Stop":
                writeNumber(102)
            #time.sleep(0.1)
    else:
        if distance < 75:
            writeNumber(105)
    print "-------------"

    # calculate the speed of the motor for displaying   
    try:
        lcd.clear()
        lcd.message('Sign:%s\nAngle deg:%d' % (sign, int(angle)))
    except IOError:
        flag = 123

    count += 1
