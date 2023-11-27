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


# define gesture_id
NONE = 0

id2mgr = {
    NONE: 'None',
    2: click_mgr,
    4: fingersnap_mgr,
}

mgr2id = {}
for id, mgr in id2mgr.items():
    mgr2id[mgr] = id


def gesture_recognizer(webcam_bgr_img):
    '''
    Get gesture from image

    webcam_bgr_img: bgr image from webcam

    return: tuple. (marked bgr image, list of recognized gesture).
            recognized gesture: (gesture_id, gesture_info)
    '''
    # preprocessing
    webcam_bgr_img = cv2.flip(webcam_bgr_img, 1) # y-axis flip
    # get recognition result
    rgb = cv2.cvtColor(webcam_bgr_img, cv2.COLOR_BGR2RGB)
    result = recognizer.get_result(rgb, timestamp_ms)
    # extract
    ret = []
    if result.gestures:
        for i in range(len(result.hand_landmarks)):
            # extract handedness, hand_landmarks, gestures
            handedness = result.handedness[i][0].display_name
            hand_landmarks = result.hand_landmarks[i]
            info = {'gesture_name': result.gestures[i][0].category_name}
            ###
            for i, (id,mgr) in enumerate(id2mgr.items()):
                if mgr.check(i, handedness, hand_landmarks, info):
                    gesture_info = {'handedness': handedness}
                    ###
                    # if isinstance(mgr.instance_list[0], GESTURE CLASS):
                    #     add info
                    ###
                    ret.append((id, gesture_info))
                # check, handler
            GestureRecognizer.draw_landmarks(rgb, hand_landmarks)
    else:
        for id, mgr in id2mgr.items():
            mgr.init('all')
        ret.append((NONE, None))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return (bgr, ret)
