'''
for presentation
'''

import cv2
import numpy as np
from gesture_recognizer.lib import GestureRecognizer
from gesture_recognizer.lib import OneHandGestureManager
from gesture_recognizer.FingerSnap import FingerSnap
from gesture_recognizer.click import Click
from gesture_recognizer.fistAndOpen import FistAndOpen


# define custom handler
text = ''

class finger_snap(FingerSnap):
    def handler(self, frame):
        global text
        text = 'finger snap'
    
class click(Click):
    def handler(self, frame):
        global text
        text = 'click'
    
class fist_and_open(FistAndOpen):
    def handler(self, frame):
        global text
        text = 'fist and open'


def main():
    '''
    Gesture recognize test from webcam
    '''
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    # Settings
    max_num_hands = 2
    SETTINGS = {
        click: {
            'DISTANCE_THRESHOLD1': 4.0,
            'DISTANCE_THRESHOLD2': 3.0,
        },
        finger_snap: {
            'DISTANCE_THRESHOLD': 3.0,
        },
        fist_and_open: {},
    }
    # create recognizer
    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=False)
    timestamp_ms = 0
    # prepare
    fingersnap_mgr = OneHandGestureManager({'Left': finger_snap(**SETTINGS[finger_snap]), 
                                            'Right': finger_snap(**SETTINGS[finger_snap])})
    click_mgr = OneHandGestureManager({'Left': click(**SETTINGS[click]), 
                                       'Right': click(**SETTINGS[click])})
    fao_mgr = OneHandGestureManager({'Left': fist_and_open(**SETTINGS[fist_and_open]),
                                     'Right': fist_and_open(**SETTINGS[fist_and_open])})
    mgr_list = [fingersnap_mgr, click_mgr, fao_mgr]

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
                    cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,0,255), thickness=3, lineType=cv2.LINE_AA)
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            else:
                for mgr in mgr_list:
                    mgr.init('all')
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
            timestamp_ms += 1
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
