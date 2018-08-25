from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import positional
import serial

def main(args):

    vs = cv2.VideoCapture(0)
    vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
    vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    # allow the camera or video file to warm up
    time.sleep(1.0)
     
    ser = serial.Serial("/dev/ttyACM0", 9600)
    ball_pos = None
    # keep looping
    while True:
        # grab the current frame
        ret, frame = vs.read()
        frame = frame[:,0:1100] 
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            break
     
        # resize the frame, blur it, and convert it to the HSV
        # color spaceme = imutils.resize(frame, width=600)
        # get only table part of image
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        ball_pos = get_ball_pos(hsv)
        if ball_pos is not None:
            str_ball_pos = str(round(ball_pos[0], 3)) + "," + str(round(ball_pos[1], 3))
            ser.write(str_ball_pos.encode())
        
        rod_pos = get_red_player_info(hsv)
        
        if args.show:
            cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    vs.release()
    ser.close() 
    # close all windows
    cv2.destroyAllWindows()

def get_ball_pos(frame):
    # construct a mask for the color "yellow", then perform
    yellowLower = (10, 52, 210)
    yellowUpper = (30, 140, 255)
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(frame, yellowLower, yellowUpper)
    #mask = cv2.erode(mask, None, iterations=1)
    #mask = cv2.dilate(mask, None, iterations=1)
    
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
        if radius > 1 and M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
     
            # only proceed if the radius meets a minimum size
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            ball_pos = positional.get_3d_point(center)
            return ball_pos

    return None

#temp code only dealing with one red rod
def get_red_player_info(frame):
    redLower = (0,120,140)
    redUpper = (255, 255,255)
    
    redrods = np.loadtxt("redrods.txt")[0]

    mask = cv2.inRange(frame, redLower, redUpper)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),key=lambda b:b[1][0]))
    vec = np.array([redrods[2]-redrods[0],redrods[3]-redrods[1]])
     
    position = (0,0,0)
    for box in boundingBoxes[0:3]:
        x,y,w,h = box
        start_point = (x,y+h//2)
        a,b = redrods[0:2]
        t = (start_point[0]*vec[0]+start_point[1]*vec[1]-a*vec[0]-b*vec[1])/(vec[0]*vec[0]+vec[1]*vec[1])
        line_point = t*vec+(a,b)
        player_pos = positional.get_3d_point(line_point)
        position += player_pos
    return position/3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--show", help="show webcam image", action="store_true")
    main(parser.parse_args())
