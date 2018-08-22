import numpy as np
import cv2

camera_mtx = np.asmatrix(np.loadtxt("cameramatrix.txt"))
camera_dist = np.loadtxt("cameradistortion.txt")

#manual calculated obj and image points
obj_points = np.array([
    (.3429, 0, 0),   #top mid
    (.3429, .59055, 0.0127), #top right
    (-.3429, .59055, 0.0127), #bottom right
    (-.3429, 0, 0), #bottom mid
    (-.3429, -.59055, 0.0127), #bottom left
    (.3429, -.59055, 0.0127), #top left
])

img_points = np.array([
    (934, 116), #top mid
    (1634, 126), #top right
    (1611, 928), #bottom right
    (921, 915), #bottom mid
    (230, 906), #bottom left
    (243, 104), #top left
    ], dtype="double")

ret, rvecs, tvecs = cv2.solvePnP(obj_points, img_points, camera_mtx, camera_dist)
#save rotation and translation
print(rvecs)
print(tvecs)
np.savetxt("rotationvector.txt",rvecs)
np.savetxt("translationvector.txt",tvecs)

