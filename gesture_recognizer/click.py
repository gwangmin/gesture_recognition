'''
Click gesture(pinching)
'''

import sys
import cv2
import numpy as np

from lib import OneHandGestureBase
from lib import OneHandGestureManager
from lib import GestureRecognizer
from lib import landmarks_num


class Click(OneHandGestureBase):
    '''
    This class represents Click Gesture

    states:
        None - nothing detected
        pinch - pinch!
        release - release
    '''
    AVAILABLE_STATES = [None, 'pinch', 'release']
    def __init__(self, DISTANCE_THRESHOLD=3.0) -> None:
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
        self.middle_tip_arr = None

    def check(self, handedness_name, hand_landmarks, info):
        thumb_tip = hand_landmarks[landmarks_num.THUMB_TIP]
        index_tip = hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks[landmarks_num.MIDDLE_FINGER_TIP]
        wrist = hand_landmarks[landmarks_num.WRIST]
        # calc dist
        thumb_tip_arr = np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z])
        index_tip_arr = np.array([index_tip.x, index_tip.y, index_tip.z])
        wrist_arr = np.array([wrist.x, wrist.y, wrist.z])
        tip_dist = np.linalg.norm(thumb_tip_arr - index_tip_arr) * 100
        wrist_index_dist = np.linalg.norm(index_tip_arr - wrist_arr) * 100

        # if state 0
        if self.state == Click.AVAILABLE_STATES[0]:
            # if thumb and index finger are close together
            if (tip_dist < self.DISTANCE_THRESHOLD):
                self.state = Click.AVAILABLE_STATES[1]
                self.wrist_index_dist = wrist_index_dist
                self.middle_tip_arr = np.array([middle_tip.x, middle_tip.y, middle_tip.z])

        # if state 1
        elif self.state == Click.AVAILABLE_STATES[1]:
            # calc middle tip dist
            cur_middle_tip_arr = np.array([middle_tip.x, middle_tip.y, middle_tip.z])
            middle_tip_dist = np.linalg.norm(self.middle_tip_arr - cur_middle_tip_arr) * 100

            # if thumb and index finger moves away from each other
            if (self.DISTANCE_THRESHOLD < tip_dist):
                # while middle finger is stopped
                # and index finger moves up
                if (middle_tip_dist < self.DISTANCE_THRESHOLD) and (self.wrist_index_dist < wrist_index_dist):
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
    Hand landmarks test from webcam
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
                    
                    d = np.linalg.norm(
                        np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]) 
                        - np.array([index_tip.x, index_tip.y, index_tip.z])) * 100
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


def click():
    '''
    Click gesture recognition with webcam
    '''
    # Settings
    max_num_hands = 2
    DISTANCE_THRESHOLD = 2.5

    recognizer = GestureRecognizer(mode=GestureRecognizer.VIDEO,
                                   max_num_hands=max_num_hands, download_model=False)
    timestamp_ms = 0

    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    click_mgr = OneHandGestureManager({'Left': Click(DISTANCE_THRESHOLD), 'Right': Click(DISTANCE_THRESHOLD)})

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
                    if click_mgr.check(handedness_name, hand_landmarks, info):
                        click_mgr.handler(handedness_name)
                    # draw landmarks
                    GestureRecognizer.draw_landmarks(frame, hand_landmarks)
            else:
                click_mgr.init('all')
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
    click()
