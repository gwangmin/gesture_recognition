'''
3 gesture test
[finger_snap, click, fist_and_open]
'''

import cv2
import numpy as np
from ..lib.recognizers import GestureRecognizer
from ..lib.gesture_templates import TwoHandGestureManager
from ..lib import cv_shortcuts as cv

from ..gestures.finger_snap import FingerSnap
from ..gestures.click import Click
from ..gestures.fist_and_open import FistAndOpen


# define custom handler
text = ''

class CustomFingerSnap(FingerSnap):
    def handler(self, frame):
        global text
        text = 'finger snap'
    
class CustomClick(Click):
    def handler(self, frame):
        global text
        text = 'click'
    
class CustomFistAndOpen(FistAndOpen):
    def handler(self, frame):
        global text
        text = 'fist and open'


def main():
    '''
    3 Gesture recognize test from webcam
    [finger_snap, click, fist_and_open]
    '''
    cam = cv2.VideoCapture(0)
    window_title = 'webcam'
    cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    time_per_frame = 1
    # Settings
    max_num_hands = 2
    SETTINGS = {
        'click': {
            'DISTANCE_THRESHOLD1': 4.0,
            'DISTANCE_THRESHOLD2': 3.0,
        },
        'finger_snap': {
            'DISTANCE_THRESHOLD': 3.0,
        },
        'fist_and_open': {},
    }
    # create recognizer
    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=False)
    timestamp_ms = 0
    # create mgr
    fs_mgr = TwoHandGestureManager({'Left': CustomFingerSnap(**SETTINGS['finger_snap']),
                                    'Right': CustomFingerSnap(**SETTINGS['finger_snap'])})
    click_mgr = TwoHandGestureManager({'Left': CustomClick(**SETTINGS['click']),
                                       'Right': CustomClick(**SETTINGS['click'])})
    fao_mgr = TwoHandGestureManager({'Left': CustomFistAndOpen(**SETTINGS['fist_and_open']),
                                     'Right': CustomFistAndOpen(**SETTINGS['fist_and_open'])})
    mgr_list = [fs_mgr, click_mgr, fao_mgr]

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get recognition result
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = recognizer.get_result(rgb, timestamp_ms)
            # extract
            ret = []
            if result.gestures:
                for i in range(len(result.hand_landmarks)):
                    # extract handedness, hand_landmarks, gestures
                    handedness_name = result.handedness[i][0].display_name
                    hand_landmarks = result.hand_landmarks[i]
                    info = {'gesture_name': result.gestures[i][0].category_name}
                    for mgr in mgr_list:
                        if mgr.check(handedness_name, hand_landmarks, info):
                            mgr.handler(handedness_name, frame)
                    cv.cv_draw_text(frame, text, cv.CV_ORGS[0], cv.CV_R)
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            else:
                text = ''
                for mgr in mgr_list:
                    mgr.init('all')
            # show frame
            cv2.imshow(window_title, frame)
            if cv2.waitKey(delay=time_per_frame) == ord('q'):
                break
            timestamp_ms += time_per_frame
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
