from transform import * # helps with perspective warp
from utils import * # functions for getting the canny image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import math
import Adafruit_CharLCD as LCD

#GPIO.setmode(GPIO.BCM)
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

# constants
RESOLUTION = (1020, 768)
STOP_TEMPLATE = cv2.imread("images/Stop_template.jpg", 1)
STOP_TEMPLATE_2 = cv2.imread("images/Stop_template_2.jpg", 1)
#STOP_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
LEFT_TEMPLATE = cv2.imread("images/Turn_Left.png", 1)
#LEFT_POINTS = [(480, 161), (480, 488), (175, 326), (217, 800), (1064, 242), (1062, 804)]
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)
#RIGHT_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
SIGN_DIM = (1280, 962)

def matches_template(warped, template):
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
    return (float(match_sum) / total_pixels >= 0.80)

def determine_sign(image, canny):
    contours = get_contours(canny)

    #display_image("canny", canny)

    # iterate through contours and find the rectangles
    approx = []
    for c in contours:
        approx = get_approx(c, 4)    # 4 vertices for rect
#    if (not approx):    # if you didn't find a rect, it's a stop
#        for c in contours:
#            approx = get_approx(c, 8)
#            if (is_sign(approx)):
#                break
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
        if (matches_template(warped, STOP_TEMPLATE) or matches_template(warped, STOP_TEMPLATE_2)):
            sign = "Stop"
            #points = STOP_POINTS
            AREA_CONST = 9
            SIGN_DIM  = [100, 100]
        if (matches_template(warped, LEFT_TEMPLATE)):
            sign = "Left"
            AREA_CONST = 6.45
            #points = LEFT_POINTS
        elif (matches_template(warped, RIGHT_TEMPLATE)):
            sign = "Right"
            AREA_CONST = 6.45        
            #points = RIGHT_POINTS
        #display_image("canny", warped)
        #draw_contours(image, approx)

        # get area of sign in image
        area = cv2.contourArea(approx)

        # get center of sign in image
        approx = np.squeeze(approx)
        x_center = (approx[0][0] + approx[1][0] + approx[2][0] + approx[3][0]) / 4
#
#        # scale important lists to match scaled image size
#        live_dim = (warped.shape[1], warped.shape[0])
#        scale = (float(SIGN_DIM[0]) / live_dim[0], float(SIGN_DIM[1]) / live_dim[1])
#        points = scale_points(scale, points)
#
#        # change points to be four corners
#        points = [(0, 0), (0, warped.shape[0]), (warped.shape[1], 0), (warped.shape[1], warped.shape[0])]
#
#        # test matrix
#        #draw_points(warped, points)
#
#        # map the points to the actual captured image
#        M[1][1] += 10^-6 # to avoid a singular matrix error
#        inverse = np.linalg.inv(M)
#        result = []
#        for point in points:
#            point = [point[0], point[1], 1] # convert points to 3D
#            point = (np.asarray(point)).reshape(3, 1)
#            new_point = (np.dot(inverse, point))
#            #new_point = np.transpose(new_point)
#            #new_point = [p / new_point[2] for p in new_point]    # normalize z
#            result.append((new_point[0][0] / new_point[2][0], -1*new_point[1][0] / new_point[2][0]))
#            print "result", result
#        draw_points(image, center)
#
#        # get the optical vector or w/e
#        if (prev_image != -1 and prev_points != -1):
#            cv2.calcOpticalFlowPyrLK(prev_image, image, prev_points, points)
#            prev_image = image
#            prev_points = points
#        else:
#            prev_image = image
#            prev_points = points
        
        # find only the good points
        #cv2.findHomography()

        # find approximate distance of sign from robot
        # just guess until you get something right

        # find angle
        image_center = (RESOLUTION[0] / 2, RESOLUTION[1] / 2)
        difference = x_center - image_center[0]    # just need x-diff
        distance = float(AREA_CONST)*(float(343)/abs(difference))*math.sqrt(area)

        if (distance == 0):
            distance = 1
        angle = math.degrees(math.atan(float(difference) / distance))

    return angle, sign

def draw_points(image, points):
    # draw dots on image
    for point in np.squeeze(points):
        image = cv2.circle(image, (int(point[0]), int(point[1])), 7, (0, 255, 0), -1)
    display_image("points", image)

def scale_points(scale, points):
    result = []
    for point in points:
        result.append((point[0] / scale[0], point[1] / scale[1]))
    return result

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = RESOLUTION
camera.awb_mode = 'flash'
rawCapture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
time.sleep(0.1)
filename = "temp.jpg"

# main loop
while (True): 
    # get the image
    camera.capture(filename)
    #filename = str(sys.argv[1])
    image = cv2.imread(filename)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect the sign type
    canny = get_canny(grey, hsv)
    angle, sign = determine_sign(image, canny)
    distance = measure_distance()
    print "DISTANCE", distance
    print sign, angle   
    # calculate the angle

    if abs(angle) > 5:
        writeNumber(int(angle))
        print "angle", angle
        time.sleep(0.5)
    else:
        writeNumber(101)
        print(101)
        time.sleep(0.1)
    if distance < 50:
        if sign == "Left":
            writeNumber(103)
            print(103)
        elif sign == "Right":
            writeNumber(104)
            print(104)
        elif sign == "Stop":
            writeNumber(102)
            print(102)
        time.sleep(0.1)
    print "-------------"

    # calculate the speed of the motor for displaying   
    try:
        lcd.clear()
        lcd.message("PATRICK")
        lcd.message('Sign:%s\nAngle deg:%d' % (sign, int(angle)))
    except IOError:
        flag = 123




################### CODE THAT I'M WORKING ON THAT MAY BE USED IN THE FUTURE???? ##########################

#
#        # scale important lists to match scaled image size
#        live_dim = (warped.shape[1], warped.shape[0])
#        scale = (float(SIGN_DIM[0]) / live_dim[0], float(SIGN_DIM[1]) / live_dim[1])
#        points = scale_points(scale, points)
#
#        # change points to be four corners
#        points = [(0, 0), (0, warped.shape[0]), (warped.shape[1], 0), (warped.shape[1], warped.shape[0])]
#
#        # test matrix
#        #draw_points(warped, points)
#
#        # map the points to the actual captured image
#        M[1][1] += 10^-6 # to avoid a singular matrix error
#        inverse = np.linalg.inv(M)
#        result = []
#        for point in points:
#            point = [point[0], point[1], 1] # convert points to 3D
#            point = (np.asarray(point)).reshape(3, 1)
#            new_point = (np.dot(inverse, point))
#            #new_point = np.transpose(new_point)
#            #new_point = [p / new_point[2] for p in new_point]    # normalize z
#            result.append((new_point[0][0] / new_point[2][0], -1*new_point[1][0] / new_point[2][0]))
#            print "result", result
#        draw_points(image, center)
#
#        # get the optical vector or w/e
#        if (prev_image != -1 and prev_points != -1):
#            cv2.calcOpticalFlowPyrLK(prev_image, image, prev_points, points)
#            prev_image = image
#            prev_points = points
#        else:
#            prev_image = image
#            prev_points = points
        
        # find only the good points
        #cv2.findHomography()

        # find approximate distance of sign from robot
        # just guess until you get something right
        #print "AREA: ", area 


