from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

def main(args):
    # define the lower and upper boundaries of the "blue"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    yellowLower = (11, 52, 211)
    yellowUpper = (37, 136, 255)

    vs = cv2.VideoCapture(0)
     
     
    # allow the camera or video file to warm up
    time.sleep(2.0)
    # keep looping
    while True:
        # grab the current frame
        ret, frame = vs.read()
     
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            break
     
        # resize the frame, blur it, and convert it to the HSV
        # color spaceme = imutils.resize(frame, width=600)
        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
     
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, yellowLower, yellowUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        center = None
     
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
     
            # only proceed if the radius meets a minimum size
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print(center)
        else:
            print("None")
        if args.show:
            cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    vs.release()
     
    # close all windows
    cv2.destroyAllWindows()
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--show", help="show webcam image", action="store_true")
    main(parser.parse_args())
