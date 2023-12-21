'''
Fist and Open gesture
'''

import sys
from typing import List, Dict, Any
from mediapipe.tasks.python.components.containers import landmark as landmark_module
import cv2
import numpy as np
from ..lib.recognizers import GestureRecognizer
from ..lib.gesture_templates import OneHandGestureBase
from ..lib.gesture_templates import TwoHandGestureManager


class FistAndOpen(OneHandGestureBase):
    '''
    This class represents Fist and Open Gesture.
    (For proper recognition, your wrist must be facing the camera and perpendicular to the floor)

    states:
        None - nothing detected
        fist - closed fist
        open - open palm
    '''
    AVAILABLE_STATES = [None, 'fist', 'open']
    def __init__(self) -> None:
        '''
        Initializer.
        '''
        self.init()
    
    def init(self) -> None:
        self.state = self.AVAILABLE_STATES[0]

    def check(self, handedness_name: str, hand_landmarks: List[landmark_module.NormalizedLandmark],
              info: Dict[str, Any]) -> bool:
        # if state 0
        if self.state == self.AVAILABLE_STATES[0]:
            # if closed_fist
            if info['gesture_name'] == GestureRecognizer.CLOSED_FIST:
                self.state = self.AVAILABLE_STATES[1]

        # if state 1
        elif self.state == self.AVAILABLE_STATES[1]:
            # if closed_fist or none
            if info['gesture_name'] in [GestureRecognizer.CLOSED_FIST, GestureRecognizer.NONE]:
                pass
            # if open_palm
            elif info['gesture_name'] == GestureRecognizer.OPEN_PALM:
                self.state = self.AVAILABLE_STATES[2]
            # if other
            else:
                self.init()

        # if last state
        elif self.state == self.AVAILABLE_STATES[2]:
            self.init()
            return True
        
        return False
    
    def handler(self) -> Any:
        '''
        Gesture handler.
        '''
        sys.exit(0)


def fist_and_open():
    '''
    Fist and Open gesture recognition from webcam.
    '''
    # Settings
    max_num_hands = 2
    download_model = True
    time_per_frame = 1

    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=download_model)
    timestamp_ms = 0

    cam = cv2.VideoCapture(0)
    window_title = 'webcam'
    cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    fao_mgr = TwoHandGestureManager({'Left': FistAndOpen(), 'Right': FistAndOpen()})

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # get results
            result = recognizer.get_result(rgb_img, timestamp_ms)
            if result.gestures:
                for i in range(len(result.hand_landmarks)):
                    # extract one hand info
                    handedness_name = result.handedness[i][0].display_name
                    hand_landmarks = result.hand_landmarks[i]
                    info = {'gesture_name': result.gestures[i][0].category_name}
                    if fao_mgr.check(handedness_name, hand_landmarks, info):
                        fao_mgr.handler(handedness_name)
                    # draw landmarks
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            else:
                fao_mgr.init('all')
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=time_per_frame) == ord('q'):
                break
            timestamp_ms += time_per_frame
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    fist_and_open()
