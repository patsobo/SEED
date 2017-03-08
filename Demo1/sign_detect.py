from transform import * # helps with perspective warp
from utils import * # functions for getting the canny image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# constants
RESOLUTION = (1020, 768)
STOP_TEMPLATE = cv2.imread("images/Stop.jpg", 1)
LEFT_TEMPLATE = cv2.imread("images/Turn_Left.png", 1)
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)

def matches_template(warped, template):
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
    return (float(match_sum) / total_pixels >= 0.85)

def determine_sign(image, canny):
    contours = get_contours(canny)
    
    # iterate through contours and find the rectangles
    for c in contours:
        approx = get_approx(c, 4)    # 4 vertices for rect
        #if ((len(approx) > 0) and is_sign(approx)):
        #    break    
#    if (not approx):    # if you didn't find a rect, it's a stop
#        for c in contours:
#            approx = get_approx(c, 8)
#            if (is_sign(approx)):
#                break

    draw_contours(image, approx)
    return "NONE"
    sign = "None"
    if (approx.any()):
        # flatten the image
        warped = four_point_transform(image, np.squeeze(approx[:4]))
    
        # convert to black and white 
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        ret, warped = cv2.threshold(warped, 90, 255, cv2.THRESH_BINARY) 
    
    
        # compare against the templates
        if (matches_template(warped, STOP_TEMPLATE)):
            sign = "Stop"    
        if (matches_template(warped, LEFT_TEMPLATE)):
            sign = "Left"
        if (matches_template(warped, RIGHT_TEMPLATE)):
            sign = "Right" 
        #display_image("canny", warped)

    return sign


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = RESOLUTION
rawCapture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
time.sleep(0.1)
filename = "temp.jpg"

# main loop
while (True): 
    # get the image
    camera.capture(filename)
    image = cv2.imread(filename)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # detect the sign type
    canny = get_canny(grey, hsv)
    sign = determine_sign(image, canny)

    # print out the sign currently displayed 
    print sign

