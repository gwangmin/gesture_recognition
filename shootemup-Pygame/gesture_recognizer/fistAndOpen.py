'''
Fist and Open gesture
'''

import sys
import cv2
import numpy as np
# non-relative import for test
if __name__ == '__main__':
    from lib import OneHandGestureBase
    from lib import OneHandGestureManager
    from lib import GestureRecognizer
    from lib import landmarks_num
else:
    from .lib import OneHandGestureBase
    from .lib import OneHandGestureManager
    from .lib import GestureRecognizer
    from .lib import landmarks_num


class FistAndOpen(OneHandGestureBase):
    '''
    This class represents Fist and Open Gesture

    states:
        None - nothing detected
        fist - closed fist
        open - open palm
    '''
    AVAILABLE_STATES = [None, 'fist', 'open']
    def __init__(self) -> None:
        '''
        Default initializer
        '''
        self.init()
    
    def init(self):
        self.state = self.AVAILABLE_STATES[0]

    def check(self, handedness_name, hand_landmarks, info):
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
    
    def handler(self):
        '''
        Gesture handler
        (mac)
        '''
        import os
        cmd = {
            'sleep': 'sleep 1',
            'hw_sleep': 'sudo shutdown -s now',
        }
        # os.system(cmd['hw_sleep'])
        sys.exit(0)


def playground():
    '''
    Gesture recognizer test from webcam
    '''
    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=2, download_model=False)
    
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    timestamp_ms = 0
    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = recognizer.get_result(img, timestamp_ms)
            # extract info
            if result.gestures:
                for i, one_hand_landmarks in enumerate(result.hand_landmarks):
                    handedness_str = f'Handedness: {result.handedness[i][0].display_name}'
                    cv2.putText(frame, handedness_str, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,0,255), thickness=3, lineType=cv2.LINE_AA)
                    
                    gesture_category = f'Gesture: {result.gestures[i][0].category_name}'
                    cv2.putText(frame, gesture_category, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,255,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    index_tip = one_hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
                    text = f'INDEX_FINGER_TIP: {int(index_tip.x*100)}, {int(index_tip.y*100)}, {int(index_tip.z*100)}'
                    cv2.putText(frame, text, (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    GestureRecognizer.draw_landmarks(frame, one_hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
            timestamp_ms += 1
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


def fistAndOpen():
    '''
    Fist and Open gesture recognition with webcam
    '''
    # Settings
    max_num_hands = 2

    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=False)
    timestamp_ms = 0

    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    fao_mgr = OneHandGestureManager({'Left': FistAndOpen(), 'Right': FistAndOpen()})

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = recognizer.get_result(rgb, timestamp_ms)
            if result.gestures:
                for i in range(len(result.hand_landmarks)):
                    # gesture
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
            if cv2.waitKey(1) == ord('q'):
                break
            timestamp_ms += 1
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    fistAndOpen()
