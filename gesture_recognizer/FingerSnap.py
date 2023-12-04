'''
finger snap gesture
'''

import sys
import time
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


DEBUG = False


class FingerSnap(OneHandGestureBase):
    '''
    This class represents Finger Snap Gesture
    (Your palm must be facing the camera for proper recognition)

    states:
        None - Nothing detected
        before - prepare finger snap
        after - after snap sounds
    '''
    AVAILABLE_STATES = [None, 'before', 'after']
    def __init__(self, DISTANCE_THRESHOLD=3.0) -> None:
        '''
        Default initializer

        DISTANCE_THRESHOLD: when Finger Snap prepare motion, thumb and middle finger
            are close together within this distance. unit: %
        '''
        self.DISTANCE_THRESHOLD = DISTANCE_THRESHOLD
        self.init()
    
    def init(self):
        self.state = FingerSnap.AVAILABLE_STATES[0]
        self.thumb_middle_dist = None
        self.wrist_middle_dist = None

    def check(self, handedness_name, hand_landmarks, info):
        thumb_tip = hand_landmarks[landmarks_num.THUMB_TIP]
        index_tip = hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks[landmarks_num.MIDDLE_FINGER_TIP]
        # calc dist
        thumb_tip_arr = np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z])
        middle_tip_arr = np.array([middle_tip.x, middle_tip.y, middle_tip.z])
        thumb_middle_dist = np.linalg.norm(thumb_tip_arr - middle_tip_arr) * 100

        # if state 0
        if self.state == FingerSnap.AVAILABLE_STATES[0]:
            # if thumb and middle finger are close together
            # and index finger is up
            if (thumb_middle_dist < self.DISTANCE_THRESHOLD) and (index_tip.y < thumb_tip.y) and (index_tip.y < middle_tip.y):
                self.state = FingerSnap.AVAILABLE_STATES[1]

        # if state 1
        elif self.state == FingerSnap.AVAILABLE_STATES[1]:
            # calc wrist dist
            wrist = hand_landmarks[landmarks_num.WRIST]
            wrist_arr = np.array([wrist.x, wrist.y, wrist.z])
            wrist_middle_dist = np.linalg.norm(wrist_arr - middle_tip_arr) * 100
            index_tip_arr = np.array([index_tip.x, index_tip.y, index_tip.z])
            index_middle_dist = np.linalg.norm(index_tip_arr - middle_tip_arr) * 100

            # if thumb and middle finger moves away from each other
            # and index finger is up
            if (self.DISTANCE_THRESHOLD < thumb_middle_dist):
                if not (index_tip.y < middle_tip.y):
                    self.init()
                if (self.thumb_middle_dist is None): # if first move, save additional progress info
                    self.thumb_middle_dist = thumb_middle_dist
                    self.wrist_middle_dist = wrist_middle_dist
                else:
                    # if thumb and middle finger moves away from each other
                    # and middle finger and wrist are close together
                    if (self.thumb_middle_dist <= thumb_middle_dist) and (wrist_middle_dist <= self.wrist_middle_dist):
                        self.state = FingerSnap.AVAILABLE_STATES[2]
                    else:
                        ### DEBUG
                        if DEBUG == True:
                            print(f'# init reason')
                            print(f'self.thumb_middle_dist, self.wrist_middle_dist: {self.thumb_middle_dist}, {self.wrist_middle_dist}')
                            print(f'thumb_middle_dist, wrist_middle_dist: {thumb_middle_dist}, {wrist_middle_dist}')
                        ###
                        self.init()

        # if last state
        elif self.state == FingerSnap.AVAILABLE_STATES[2]:
            self.init()
            if info['gesture_name'] != GestureRecognizer.CLOSED_FIST:
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
    Hand landmark test from webcam
    '''
    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=2, download_model=False)
    timestamp_ms = 0

    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = recognizer.get_result(rgb, timestamp_ms)
            # extract info
            if result.gestures:
                for hand_landmarks in result.hand_landmarks:
                    thumb_tip = hand_landmarks[landmarks_num.THUMB_TIP]
                    index_tip = hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks[landmarks_num.MIDDLE_FINGER_TIP]

                    text = f'THUMB_TIP: {int(thumb_tip.x*100)}, {int(thumb_tip.y*100)}, {int(thumb_tip.z*100)}'
                    cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,0,255), thickness=3, lineType=cv2.LINE_AA)
                    
                    text = f'INDEX_FINGER_TIP: {int(index_tip.x*100)}, {int(index_tip.y*100)}, {int(index_tip.z*100)}'
                    cv2.putText(frame, text, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,255,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    text = f'MIDDLE_FINGER_TIP: {int(middle_tip.x*100)}, {int(middle_tip.y*100)}, {int(middle_tip.z*100)}'
                    cv2.putText(frame, text, (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    d = np.linalg.norm(np.array([thumb_tip.x,thumb_tip.y,thumb_tip.z]) - np.array([middle_tip.x,middle_tip.y,middle_tip.z])) * 100
                    text = f'dist: {d}'
                    cv2.putText(frame, text, (10,120), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
            timestamp_ms += 1
    # exit
    recognizer.close()
    cam.release()
    cv2.destroyAllWindows()


def finger_snap():
    '''
    Finger Snap recognition with webcam
    '''
    # Settings
    max_num_hands = 2
    DISTANCE_THRESHOLD = 3

    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=False)
    timestamp_ms = 0

    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    fingersnap_mgr = OneHandGestureManager({'Left': FingerSnap(DISTANCE_THRESHOLD), 'Right': FingerSnap(DISTANCE_THRESHOLD)})

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
                    if fingersnap_mgr.check(handedness_name, hand_landmarks, info):
                        fingersnap_mgr.handler(handedness_name)
                    # draw landmarks
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            else:
                fingersnap_mgr.init('all')
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
    finger_snap()
