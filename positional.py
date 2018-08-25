import cv2
import numpy as np
import argparse

def undistort(point):
    cam_mtx, cam_dist, tran_vec, rot_vec = get_camera_info()
    point = np.array([[[point[0], float(point[1])]]])	   
    scale_mtx = np.matrix([[.625, 0, 0], [0, 5/9, 0], [0, 0, 1]])
    cam_mtx = scale_mtx * cam_mtx
    #TODO look into use getOptimalNewCameraMatrix
    return cv2.undistortPoints(point, cam_mtx, cam_dist, P = cam_mtx)

def get_vector(point):
    cam_mtx, cam_dist, tran_vec, rot_vec = get_camera_info()
    scale_mtx = np.matrix([[.5, 0, 0], [0, .5, 0], [0, 0, 1]])
    cam_mtx = scale_mtx * cam_mtx
    undist = undistort(point)
    proj_inv = np.linalg.pinv(cam_mtx)
    #backproject using pseudo inverse
    ray = proj_inv*np.matrix([[undist[0][0][0]],[undist[0][0][1]],[1]])
    #convert from homegenous to cartesian
    return ray
def get_camera_info():
    camera_mtx = np.array(np.loadtxt("calibration/cameramatrix.txt")).reshape(3,3)
    camera_dist = np.array(np.loadtxt("calibration/cameradistortion.txt"))
    tran_vec = np.array(np.loadtxt("calibration/translationvector.txt"))
    rot_vec = np.array(np.loadtxt("calibration/rotationvector.txt"))
    return (camera_mtx, camera_dist, tran_vec, rot_vec)

def get_3d_point(point2d):
    '''cam_pos = get_camera_pos()
    #flip sign because calibration flipped along z axis
    cam_pos[0,2] = -cam_pos[0,2]
    ray = get_vector(point2d).reshape(-1,3)
    normal = (0,0,1)
    t = (np.dot((0,0,z)-cam_pos,normal))/np.dot(ray,normal)
    ground_pos = cam_pos + t*ray'''
    point2d = undistort(point2d)
    point2d -= (119,60)
    point3d = np.array([point2d.item(0)/(980-119),point2d.item(1)/(566-60),0])
    point3d = point3d * (1.1811,0.6858,0)
    point3d -= (0.59055, .3429, 0)
    return point3d

def get_camera_pos():
    cam_mtx, cam_dist, trans_vec, rot_vec = get_camera_info()
    rot_mtx, _ = cv2.Rodrigues(rot_vec)
    trans_vec = trans_vec.reshape(3,1)
    return np.dot(-rot_mtx.T,trans_vec.reshape(3,1)).reshape(1,3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    args = parser.parse_args()
    print(get_point((args.x,args.y)))
