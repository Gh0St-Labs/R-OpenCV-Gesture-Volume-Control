import cv2 as cv
import time
import numpy as np
import QuantHandTracking as QTH
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Setting the width and height for our webcam capture
# <><><><><><><><><><><><><><><><><><><><><><><><>
camWidth = 648
canHeight = 488
# <><><><><><><><><><><><><><><><><><><><><><><><>

# For <><><> tweaking <><><> the volume from Python
# <><> RULE <><> This module is not nationaly or globally recognized, so there is no use in learning it.
# JUST COPY PASTE THIS CODE AND DO WHAT IS DONE BELOW!
# WE ONLY NEED TWO THINGS FROM THESE COPY PASTED CODE, 
# 1. volume.GetVolumeRange()
# 2. volume.SetMasterVolumeLevel(-25.25, None)
# <><> DO NOT MESS WITH THESE LINES OF CODE FROM HERE... THESE ARE FOR THE CONFIGURATIONS.
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# <><> ...TILL HERE.
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
theVolumeRange = volume.GetVolumeRange()
# The 'volume.getVolumeRange' returns a tuple of three values. The first value is -65.25, second is 0.0 
# and the third is 0.03674. WE ARE NOT INTERESTED IN THE THIRD VALUE, SO SKIP THE TOPIC!
# -65.25 indicates ABSOLUTELY NO VOLUME, 0
# 0.0 indicates a FULL VOLUME, 100.
# So every volume from our perspective should be added with -65.25 for the pycaw library to interpret
minVolume = theVolumeRange[0] # Getting -65.25 which is the bare minimum volume from pycaw's perspective
maxVolume = theVolumeRange[1] # Getting 0.0 which is the maximum volume in the perspective of pycaw
# <><><> volume tweaking ends here <><><>

video = cv.VideoCapture(0)

# While setting the capture's width and height, the first parameter denotes the ID of the property we're about 
# to set.
# Number 3 is for the width and number 4 is for the height. 
video.set(3, camWidth)
video.set(4, canHeight)

previousTime = 0
# Setting the initial maximum height so that it does not exceed any height limits than the sound bar rectangle
# Setting up the Hand Detector from the QuantHandTracking Module
# We are changing the detection confidence to a much stronger value so the detection can be much more strict
# and more effective
handDetector = QTH.HandDetector(minDetectionConfidence=0.7)

while True:
    bool, frame = video.read()

    # Detect hands
    handDetector.findHands(frame)

    # Find Positions
    landmarkList = handDetector.findLandmark(frame, draw=False)

    # Repossess two points out of the 21 points landmark-ed for accessing the volume controls.
    if len(landmarkList) != 0:
        # Point 1. Tip of the thumb
        thumb_tip = landmarkList[4]
        x1 = thumb_tip[1]
        y1 = thumb_tip[2]
        cv.circle(frame, (x1, y1), radius=10, color=(255,255,0), thickness=-1)
        
        # Point 2. Tip of the index
        index_tip = landmarkList[8]
        x2 = index_tip[1]
        y2 = index_tip[2]
        cv.circle(frame, (index_tip[1], index_tip[2]), radius=10, color=(255,255,0),thickness=-1)
        # The 4th point on the hand refers to the tip of the thumb, so we index it out of it.

        # Add a line between the two points
        cv.line(frame, (thumb_tip[1], thumb_tip[2]), (index_tip[1], index_tip[2]), color=(0,255,255), 
                thickness=3)        
        # Acquiring the middle point of the line created using the formula x1+x2 / 2 and y1+y2 / 2
        centerx = (x1 + x2) // 2
        centery = (y1 + y2) // 2

        # Circling the middle point on the line
        cv.circle(frame, (centerx, centery), 10, (0,255,255), -1)

        # Finding the length of the points from the middle to secure the value which should be set for the 
        # volume
        lenght = math.hypot(x1 - x2, y1 - y2)
        # Using the hypotenuse method form the 'math' module can help cop the lenght between two co-ordinates
        # using it's x and y point values.
        # print(lenght)

        # The maximum lenght is about 350 pixels and the minimum is somewhere around 40 to 45.
        if lenght < 50:
            cv.circle(frame, (centerx, centery), 10, (0,0,255), -1)
            cv.putText(frame, 'Lowest Volume Reached!', (centerx + 15, centery), cv.FONT_HERSHEY_PLAIN, 2, 
                       (0,0,255), 2)        
        
        # Conversion of the lenght of the points to volume ranges
        # Point Range ('lenght') -> 50 (lowest) - 300 (highest)
        # Volume Range ('theVolumeRange') -> -65.25 (lowest) - 0 (highest)

        # <><><> RULE <><><> Conversion can easily be done using Numpy
        vol = np.interp(lenght,[50, 300], [minVolume, maxVolume])
        # The first argument is the instance containing the values which have to be changed
        # The second argument is the range of values that are specifically needed to be changed 
        # in the instance, WRAPPED IN A LIST.
        # The third argument is again a range of values which are to be converted from
        # the range of values specifically taken from the instance. WRAP IT IN A LIST.

        # The Volume bar value conversion
        volBar = np.interp(lenght, [50, 300], [400, 150])

        # Volume Percentage Conversion
        volPercentage = np.interp(lenght, [50, 300], [0, 100])

        # Circle Radius Conversion
        volCircle = np.interp(lenght, [50, 300], [10,30])

        
        # Set the volume (This line of code has been taken from the copy - pasted code.)
        # Refer here -> https://github.com/AndreMiras/pycaw <- Make sure you scroll down till the end
        # <><> TAKEN FROM 'volume tweaking (line 15) <><>
        volume.SetMasterVolumeLevel(vol, None)

        # Set a custom rectange which change proportionatily to the change in volume.
        # Sound Bar Rectangle
        cv.rectangle(frame, (50, 150), (85,400), (255,255,255), 2)
        # <><> RULE <><> Point 2 values are actually not calibrated from the window but from point 1
        # Change in volume rectangle
        cv.rectangle(frame, (50, int(volBar)), (85, 400), color=(255,0,0), thickness=-1)
        
        # Adding my Trademark -> VolCircle™
        cv.circle(frame, (580, 50), 10, (255,255,255), -1)
        cv.circle(frame, (580, 50), int(volCircle), (0,255,0), 2)

        # Add the percentage to the Volume Bar
        cv.putText(frame, f'{int(volPercentage)}%', (95, int(volBar)), cv.FONT_HERSHEY_PLAIN, 2, 
                   (255,255,255), 2)

    # Scaling the FPS
    currentTime = time.time()
    FPS = 1 / (currentTime - previousTime)
    previousTime = currentTime

    cv.putText(frame, f'FPS: {int(FPS)}', (10,40), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)

    cv.imshow('Frame', frame)
    cv.waitKey(1)

    if cv.waitKey(20) & 0xFF==ord('f'):
        break
        video.release()
        cv.destroyAllWindows()