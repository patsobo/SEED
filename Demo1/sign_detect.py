from transform import * # helps with perspective warp
from utils import * # functions for getting the canny image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# constants
RESOLUTION = (1020, 768)
STOP_TEMPLATE = cv2.imread("images/Stop.jpg", 1)
STOP_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
LEFT_TEMPLATE = cv2.imread("images/Turn_Left.png", 1)
LEFT_POINTS = [(480, 161), (480, 488), (175, 326), (217, 800), (1064, 242), (1062, 804)]
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)
RIGHT_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
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
    approx = []
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
    points = []
    if (len(np.squeeze(approx)) >= 4):
        # flatten the image
        M, warped = four_point_transform(image, np.squeeze(approx[:4]))

        # convert to black and white 
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        ret, warped = cv2.threshold(warped, 90, 255, cv2.THRESH_BINARY) 
    
        # compare against the templates
        if (matches_template(warped, STOP_TEMPLATE)):
            sign = "Stop"
            points = STOP_POINTS
        if (matches_template(warped, LEFT_TEMPLATE)):
            sign = "Left"
            points = LEFT_POINTS
        elif (matches_template(warped, RIGHT_TEMPLATE)):
            sign = "Right"
            points = RIGHT_POINTS
            draw_points(RIGHT_TEMPLATE, RIGHT_POINTS)
        #display_image("canny", warped)
        #draw_contours(image, approx)

        # scale important lists to match scaled image size
        live_dim = (warped.shape[1], warped.shape[0])
        scale = (float(SIGN_DIM[0]) / live_dim[0], float(SIGN_DIM[1]) / live_dim[1])
        points = scale_points(scale, points)

        # test matrix
        print "M", M

        # map the points to the actual captured image
        M[1][1] += 10^-6 # to avoid a singular matrix error
        inverse = np.linalg.inv(M)
        result = []
        for point in points:
            point = (point[0], point[1], 0) # convert points to 3D
            point = np.asarray(point)
            new_point = np.transpose(np.dot(inverse, point))
            result.append((new_point[0], new_point[1]))
        print "points on pic", result
        draw_points(image, result)
       
    return sign

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
rawCapture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
time.sleep(0.1)
filename = "temp.jpg"

# main loop
while (True): 
    # get the image
    #camera.capture(filename)
    filename = str(sys.argv[1])
    image = cv2.imread(filename)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # detect the sign type
    canny = get_canny(grey, hsv)
    sign = determine_sign(image, canny)
    
    # calculate the angle

    # print out the sign currently displayed 
    print sign

