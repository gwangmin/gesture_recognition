'''
Click gesture(pinching)
'''

import sys
import cv2
import numpy as np

from lib import OneHandGestureBase
from lib import OneHandGestureManager
from lib import HandLandmarker
from lib import landmarks_num
from lib import draw_landmarks


class Click(OneHandGestureBase):
    '''
    This class represents Click Gesture

    states:
        None - nothing detected
        pinch - pinch!
        release - release
    '''
    AVAILABLE_STATES = [None, 'pinch', 'release']
    def __init__(self, DISTANCE_THRESHOLD=2.0) -> None:
        '''
        Default initializer

        DISTANCE_THRESHOLD: thumb tip and index finger tip distance threshold.
            when pinch. unit: %
        '''
        self.DISTANCE_THRESHOLD = DISTANCE_THRESHOLD
        self.init()
    
    def init(self):
        self.state = Click.AVAILABLE_STATES[0]
        self.wrist_index_dist = None

    def check(self, handedness, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[landmarks_num.THUMB_TIP]
        index_tip = hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP]
        wrist = hand_landmarks.landmark[landmarks_num.WRIST]
        # calc dist
        thumb_tip_arr = np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z])
        index_tip_arr = np.array([index_tip.x, index_tip.y, index_tip.z])
        tip_dist = np.linalg.norm(thumb_tip_arr - index_tip_arr) * 100
        wrist_arr = np.array([wrist.x, wrist.y, wrist.z])
        wrist_index_dist = np.linalg.norm(index_tip_arr - wrist_arr) * 100

        # if state 0
        if self.state == Click.AVAILABLE_STATES[0]:
            # if thumb and index finger are close together
            if (tip_dist < self.DISTANCE_THRESHOLD):
                self.state = Click.AVAILABLE_STATES[1]
                self.wrist_index_dist = wrist_index_dist

        # if state 1
        elif self.state == Click.AVAILABLE_STATES[1]:
            # if thumb and index finger moves away from each other
            if self.DISTANCE_THRESHOLD < tip_dist:
                if self.wrist_index_dist < wrist_index_dist:
                    self.state = Click.AVAILABLE_STATES[2]
                else:
                    self.init()

        # if last state
        elif self.state == Click.AVAILABLE_STATES[2]:
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
    Hand landmark detection test from webcam
    '''
    hand_landmarker = HandLandmarker(max_num_hands=1,
                                      min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand_landmarker.get_result(img)
            # extract info
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    thumb_tip = hand_landmarks.landmark[landmarks_num.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[landmarks_num.MIDDLE_FINGER_TIP]

                    text = f'THUMB_TIP: {int(thumb_tip.x*100)}, {int(thumb_tip.y*100)}, {int(thumb_tip.z*100)}'
                    cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,0,255), thickness=3, lineType=cv2.LINE_AA)
                    
                    text = f'INDEX_FINGER_TIP: {int(index_tip.x*100)}, {int(index_tip.y*100)}, {int(index_tip.z*100)}'
                    cv2.putText(frame, text, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (0,255,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    text = f'MIDDLE_FINGER_TIP: {int(middle_tip.x*100)}, {int(middle_tip.y*100)}, {int(middle_tip.z*100)}'
                    cv2.putText(frame, text, (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    d = np.linalg.norm(
                        np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]) 
                        - np.array([index_tip.x, index_tip.y, index_tip.z])) * 100
                    text = f'dist: {d}'
                    cv2.putText(frame, text, (10,120), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    
                    draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()


def click():
    '''
    Click gesture recognition with webcam
    '''
    # Settings
    ## landmarker settings
    max_num_hands = 1
    min_detection_confidence = 0.5
    min_tracking_confidence = 0.5
    ## gesture settings
    DISTANCE_THRESHOLD = 2

    hand_landmarker = HandLandmarker(max_num_hands=max_num_hands,
                                     min_detection_confidence=min_detection_confidence,
                                     min_tracking_confidence=min_tracking_confidence)
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img
    fingersnap_mgr = OneHandGestureManager([Click(DISTANCE_THRESHOLD)] * max_num_hands)

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
    click()
