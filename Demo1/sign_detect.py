from transform import * # helps with perspective warp
from utils import * # functions for getting the canny image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# constants
RESOLUTION = (1020, 768)
STOP_TEMPLATE = cv2.imread("images/Stop.jpg", 1)
LEFT_TEMPLATE = cv2.imread("images/Turn_Left.png", 1)
LEFT_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)
RIGHT_POINTS = [(480, 161), (480, 488), (175, 326), (217, 800), (1064, 242), (1062, 804)]
SIGN_DIM = (1280, 962)

def matches_template(warped, template):
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    ret, template = cv2.threshold(template, 90, 255, cv2.THRESH_BINARY)
    template = cv2.resize(template, (warped.shape[1], warped.shape[0])) # x and y lengths of your warped image (resize the template)
    total_pixels = warped.shape[0]*warped.shape[1]
    if (total_pixels < 200*200):
        return False
    match_sum = 0
    for i in range(0, warped.shape[0]):    
        for j in range(0, warped.shape[1]):
            pixel = template[i][j]
            my_pixel = warped[i][j]
            if (pixel == my_pixel):
                match_sum += 1    
    return (float(match_sum) / total_pixels >= 0.75)

def determine_sign(image, canny):
    contours = get_contours(canny)
    
    # iterate through contours and find the rectangles
    for c in contours:
        approx = get_approx(c, 4)    # 4 vertices for rect
#    if (not approx):    # if you didn't find a rect, it's a stop
#        for c in contours:
#            approx = get_approx(c, 8)
#            if (is_sign(approx)):
#                break
    #draw_contours(image, approx)
    #draw_contours(image, approx)
    sign = "None"
    if (len(np.squeeze(approx)) >= 4):
        # flatten the image
        M, warped = four_point_transform(image, np.squeeze(approx[:4]))
    
        # convert to black and white 
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        ret, warped = cv2.threshold(warped, 90, 255, cv2.THRESH_BINARY) 
    
        # compare against the templates
        if (matches_template(warped, STOP_TEMPLATE)):
            sign = "Stop"    
        if (matches_template(warped, LEFT_TEMPLATE)):
            sign = "Left"
        elif (matches_template(warped, RIGHT_TEMPLATE)):
            sign = "Right" 
        #display_image("canny", warped)
        #draw_contours(image, approx)
        live_dim = (warped.shape[1], warped.shape[0])
        scale = (SIGN_DIM[0] / live_dim[0], (SIGN_DIM[1] / live_dim[1]))
        inverse = np.linalg.inv(M)
        result = np.multiply(
        print scale, M
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
    
    # calculate the angle

    # print out the sign currently displayed 
    print sign

