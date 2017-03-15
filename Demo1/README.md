# Demo 1 Computer Vision

This repository houses all the code for the computer vision portion of Demo 1 for SEED lab.  All the code is written with Python.  Much of the code in this directory is unnecessary for the final project.  Here are the important files, and a quick description:

### sign_detect.py

The main script that is run to detect a sign and the angle of that sign using the mounted Pi camera.

### utils.py

This script contains a smattering of functions that sign_detect.py uses for simple, modular tasks.  These functions are put in a separate file to keep the main script as clean as possible.

### transform.py

Provided code that helps with creating an perspective warp on an image.  In this case, I run the contour with the sign through the function provided in this script to get a flattened view of the sign, for comparing against the template

### images/

The only important pictures are Turn_Left.png, Turn_Right.png, Stop_template.jpg, and Stop_template_2.jpg.  These are the templates used to compare against the live image to see if a sign was actually detected.

### Final comments

Everything else isn't really pertinent to the project, especially scripts in the auxiliary/ directory.  Make sure you have a Pi camera and OpenCV installed.
