'''
api for LDH game
'''

import cv2
import numpy as np
from lib import GestureRecognizer
from lib import landmarks_num
from lib import OneHandGestureManager

from FingerSnap import FingerSnap
from click import Click
from fistAndOpen import FistAndOpen


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
fao_mgr = OneHandGestureManager([FistAndOpen()] * max_num_hands)


# define gesture_id
NONE = 0
FIST_MOVE = 3
id2mgr = {
    1: fao_mgr,
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
    global timestamp_ms
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
            # fist_move
            if info['gesture_name'] == GestureRecognizer.CLOSED_FIST:
                index_tip = hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
                x = round(index_tip.x, 2)
                y = round(index_tip.y, 2)
                z = round(index_tip.z, 2)
                gesture_info = {'handedness': handedness, 'xyz': (x, y, z)}
                ret.append((FIST_MOVE, gesture_info))
            # other gestures
            for id, mgr in id2mgr.items():
                if mgr.check(i, handedness, hand_landmarks, info):
                    gesture_info = {'handedness': handedness}
                    ret.append((id, gesture_info))
            GestureRecognizer.draw_landmarks(rgb, hand_landmarks)
    else:
        for id, mgr in id2mgr.items():
            mgr.init('all')
    if not ret:
        ret.append((NONE, None))
    timestamp_ms += 1 #
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return (bgr, ret)


def test():
    '''
    func test from webcam
    '''
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # func call
            result = gesture_recognizer(frame)

            text = f'{result[1]}'
            cv2.putText(result[0], text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,0,255), thickness=3, lineType=cv2.LINE_AA)
            
            # show frame
            cv2.imshow('webcam', result[0])
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test()
