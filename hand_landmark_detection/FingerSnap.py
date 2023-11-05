import sys
import time
import cv2
import numpy as np

from lib import OneHandGestureBase
from lib import OneHandGestureManager
from lib import HandLandmarker
from lib import landmarks_num
from lib import draw_landmarks


class FingerSnap(OneHandGestureBase):
    '''
    This class represents Finger Snap Gesture

    states:
        None - Nothing detected
        before - prepare finger snap
        after - after snap sounds
    '''
    AVAILABLE_STATES = [None, 'before', 'after']
    def __init__(self, DISTANCE_THRESHOLD=3.0, KEEP_DURATION=0.05) -> None:
        '''
        Default initializer

        DISTANCE_THRESHOLD: when Finger Snap prepare motion, thumb and middle finger
            are close together within this distance. unit: %
        KEEP_DURATION: gesture keep time. unit: second(s)
        '''
        self.DISTANCE_THRESHOLD = DISTANCE_THRESHOLD
        self.KEEP_DURATION = KEEP_DURATION
        self.init()
    
    def init(self):
        self.state = FingerSnap.AVAILABLE_STATES[0]
        self.finger_dist = None
        self.wrist_middle_dist = None

    def check(self, handedness, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[landmarks_num.THUMB_TIP]
        index_tip = hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[landmarks_num.MIDDLE_FINGER_TIP]
        # calc dist
        thumb_tip_arr = np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z])
        middle_tip_arr = np.array([middle_tip.x, middle_tip.y, middle_tip.z])
        finger_dist = np.linalg.norm(thumb_tip_arr - middle_tip_arr) * 100 #

        # if state 0
        if self.state == FingerSnap.AVAILABLE_STATES[0]:
            # if thumb and middle finger are close together
            # and index finger is up
            if (finger_dist < self.DISTANCE_THRESHOLD) and (index_tip.y < thumb_tip.y) and (index_tip.y < middle_tip.y):
                self.state = FingerSnap.AVAILABLE_STATES[1]

        # if state 1
        elif self.state == FingerSnap.AVAILABLE_STATES[1]:
            # calc wrist dist
            wrist = hand_landmarks.landmark[landmarks_num.WRIST]
            wrist_arr = np.array([wrist.x, wrist.y, wrist.z])
            wrist_middle_dist = np.linalg.norm(wrist_arr - middle_tip_arr) * 100 #

            # if thumb and middle finger moves away from each other
            # and middle finger and wrist are close together
            # for KEEP_DURATION secs
            if (self.DISTANCE_THRESHOLD < finger_dist): # moves away
                if (self.finger_dist is None) and (self.wrist_middle_dist is None): # save additional progress info
                    self.finger_dist = finger_dist
                    self.wrist_middle_dist = wrist_middle_dist
                else:
                    if (self.finger_dist <= finger_dist) and (wrist_middle_dist <= self.wrist_middle_dist):
                        self.state = FingerSnap.AVAILABLE_STATES[2]
                    else:
                        ### DEBUG
                        print(f'# init reason')
                        print(f'self.finger_dist, self.wrist_middle_dist: {self.finger_dist}, {self.wrist_middle_dist}')#
                        print(f'finger_dist, wrist_middle_dist: {finger_dist}, {wrist_middle_dist}')#
                        ###
                        self.init()

        # if last state
        elif self.state == FingerSnap.AVAILABLE_STATES[2]:
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


def finger_snap():
    '''
    Finger Snap recognition with webcam
    '''
    # Settings
    ## landmarker settings
    max_num_hands = 1
    min_detection_confidence = 0.5
    min_tracking_confidence = 0.5
    ## gesture settings
    DISTANCE_THRESHOLD = 3
    KEEP_DURATION = 0.05

    hand_landmarker = HandLandmarker(max_num_hands=max_num_hands,
                                     min_detection_confidence=min_detection_confidence,
                                     min_tracking_confidence=min_tracking_confidence)
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    fingersnap_mgr = OneHandGestureManager([FingerSnap(DISTANCE_THRESHOLD, KEEP_DURATION)] * max_num_hands)

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand_landmarker.get_result(img)
            if result.multi_handedness:
                for i in range(len(result.multi_hand_landmarks)):
                    # gesture
                    if fingersnap_mgr.check(i, result):
                        fingersnap_mgr.handler(i)
                    # draw landmarks
                    draw_landmarks(frame, result.multi_hand_landmarks[i])
            else:
                fingersnap_mgr.init('all')
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    finger_snap()
