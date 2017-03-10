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
RIGHT_POINTS = [(217, 245), (217, 800), (800, 161), (800, 485), (1105, 326)]
RIGHT_TEMPLATE = cv2.imread("images/Turn_Right.png", 1)
LEFT_POINTS = [(480, 161), (480, 488), (175, 326), (217, 800), (1064, 242), (1062, 804)]
SIGN_DIM = (1280, 962)

def draw_points(image, points):
    # draw dots on image
    for point in np.squeeze(points):
        image = cv2.circle(image, (int(point[0]), int(point[1])), 7, (0, 255, 0), -1)
    display_image("points", image)


draw_points(RIGHT_TEMPLATE, RIGHT_POINTS)
draw_points(LEFT_TEMPLATE, LEFT_POINTS)


