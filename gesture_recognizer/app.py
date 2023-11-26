'''
api for LDH game
'''

import cv2
import numpy as np
from lib import GestureRecognizer
from lib import OneHandGestureManager

from FingerSnap import FingerSnap
from click import Click


# Settings
max_num_hands = 2
DISTANCE_THRESHOLD = {
    Click: 3.0,
    FingerSnap: 3.0,
}
# create recognizer
recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                               max_num_hands=max_num_hands, download_model=True)
timestamp_ms = 0
# prepare
fingersnap_mgr = OneHandGestureManager([FingerSnap(DISTANCE_THRESHOLD[FingerSnap])] * max_num_hands)
click_mgr = OneHandGestureManager([Click(DISTANCE_THRESHOLD[Click])] * max_num_hands)
mgrs = [fingersnap_mgr, click_mgr]

# define gesture_id
gesture_id = {
    'None': 0,
    Click: 2,
    FingerSnap: 4,
}


def gesture_recognizer(webcam_bgr_img):
    '''
    Get gesture from image

    webcam_bgr_img: bgr image from webcam

    return: tuple. (gesture_id, gesture_info)
    '''
    # preprocessing
    webcam_bgr_img = cv2.flip(webcam_bgr_img, 1) # y-axis flip
    # get recognition result
    rgb = cv2.cvtColor(webcam_bgr_img, cv2.COLOR_BGR2RGB)
    result = recognizer.get_result(rgb, timestamp_ms)
    # extract
    if result.gestures:
        for i in range(len(result.hand_landmarks)):
            handedness = result.handedness[i][0].display_name
            hand_landmarks = result.hand_landmarks[i]
            info = {'gesture_name': result.gestures[i][0].category_name}
            ###
    else:
        for mgr in mgrs:
            mgr.init('all')
        return (gesture_id['None'], None)
