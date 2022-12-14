# import the opencv library
import cv2
import time
import numpy as np
import imageio
from datetime import datetime
BUFF_SIZE = 30
opticalFlowVisualization = False
viewOnActivation = True
# define a video capture object
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set to the maximum the camera can See
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#vid.set(cv2.CAP_PROP_FPS, 30)

# Denoise the camera so the optical flow can work as a sensor
def adapt(image):
    gray =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  #Make Gray
    kernel = np.ones((5, 5), np.uint8)
    inv_image = (255 - gray)                        #Invert colors
    #Remove a bit of noise
    img_erosion = cv2.erode(inv_image, kernel, iterations=1)
    blur = cv2.GaussianBlur(img_erosion, (0, 0), sigmaX=22, sigmaY=22)
    #cv2.imshow('morph', image)
    #cv2.waitKey(1)
    return blur

frames = []
print("Started Camera")
while (True):
    #Get Camera
    ret, frame = vid.read()
    frames.append(frame)
    prvs = adapt(frame)

    ret, frame = vid.read()
    frames.append(frame)
    next = adapt(frame)
    flow = cv2.calcOpticalFlowFarneback(prev = prvs,next = next,flow =  None,pyr_scale =  0.5,levels =  3,winsize =  50,iterations = 3, poly_n  = 7, poly_sigma =  1.5,flags = 0)
    avg_dif = np.average(flow) * 10 ** 6
    if opticalFlowVisualization:  # Set this variable to True if you want to see the optical flow and check the flow values
        hsv = np.zeros_like(frame)
        hsv[..., 1] = 255
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        print(avg_dif)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        cv2.waitKey(1)

    prvs = next

    #Capture gifs of events that are above the optical flow threshold

    if(avg_dif>2.5):
        video_name = str(datetime.fromtimestamp(time.time())) #Set video name at time of saving
        for _ in range(200): #Set how many frames you want saved after an event has happened
            ret, frame = vid.read()
            frames.append(frame)
            if viewOnActivation:
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        if viewOnActivation:
            cv2.destroyAllWindows()
        print("Saving Video",video_name,end="")
        imageio.mimsave('movie_'+video_name+'.gif', frames)
        print("...Done")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frames = frames[-100:] #Set how many frames you want saved before the event happened

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
