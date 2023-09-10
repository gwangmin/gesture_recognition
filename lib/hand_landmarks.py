'''
Hand landmarks detection
'''


import time
import sys
import mediapipe as mp
import numpy as np
import cv2


landmarks_num = mp.solutions.hands.HandLandmark # Landmark index

class HandLandmarker:
    '''
    Hand landmarker using mp.solutions

    mp.solutions.hands: https://github.com/google/mediapipe/blob/master/docs/solutions/hands.md
    '''

    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5) -> None:
        '''
        Init

        static_image_mode: image source is static? or stream?
        max_num_hands: Maximum number of hands to detect.
        min_detection_confidence: Minimum confidence value ([0.0, 1.0])
            for hand detection to be considered successful.
        min_tracking_confidence: Minimum confidence value ([0.0, 1.0])
            for the hand landmarks to be considered tracked successfully.
        '''
        self.landmarker = mp.solutions.hands.Hands(static_image_mode=static_image_mode,
                                                   max_num_hands=max_num_hands,
                                                   min_detection_confidence=min_detection_confidence,
                                                   min_tracking_confidence=min_tracking_confidence)

    def get_result(self, rgb_img):
        '''
        Process rgb_img and return result
        
        - result
            result.multi_handedness: list of handedness obj
            result.multi_hand_landmarks: list of one hand landmarks obj(in image coord.). [0,1]
            result.multi_hand_world_landmarks: list of one hand landmarks obj(in world coord.)
        '''
        return self.landmarker.process(rgb_img)
    
    def close(self):
        '''
        Release resources
        '''
        self.landmarker.close()


# Drawing & Plotting
drawing_helper = mp.solutions.drawing_utils
drawing_styles = mp.solutions.drawing_styles

# hand landmark module
hands = mp.solutions.hands
def draw_landmarks(img, hand_landmark_obj):
    '''
    Draw one hand landmarks.

    img: rgb or bgr. no matter.
    hand_landmark_obj: one hand landmark obj.
    '''
    # draw
    drawing_helper.draw_landmarks(img, hand_landmark_obj, hands.HAND_CONNECTIONS,
                                  drawing_styles.get_default_hand_landmarks_style(),
                                  drawing_styles.get_default_hand_connections_style())

def plot_world_landmarks(hand_world_landmark_obj):
    '''
    (accuracy is very low)

    Plot one hand landmarks in world coord.

    hand_world_landmark_obj: one hand landmark obj in world coord.
    '''
    # draw
    drawing_helper.plot_landmarks(hand_world_landmark_obj, hands.HAND_CONNECTIONS,
                                  azimuth=5)


class FingerSnap:
    '''
    This class represents one hand's Thanos Finger Snap Gesture

    states:
        None - Nothing detected
        before - prepare finger snap
        after - after snap sounds
    '''
    AVAILABLE_STATES = [None, 'before', 'after']
    def __init__(self, DISTANCE_THRESHOLD=2) -> None:
        '''
        Default initializer

        DISTANCE_THRESHOLD: when Finger Snap prepare motion, thumb and middle finger
            are close together within this distance. unit: percentage
        '''
        self.DISTANCE_THRESHOLD = DISTANCE_THRESHOLD
        self.init()
    
    def init(self):
        '''
        Initialize self
        '''
        self.state = FingerSnap.AVAILABLE_STATES[0]
        self.dist = None
        self.after_time = None

    def check(self, handedness, hand_landmarks):
        '''
        Check hand landmarks. return True, if gesture recognized.

        handedness: one handedness
        hand_landmarks: one hand landmarks
        '''
        thumb_tip = hand_landmarks.landmark[landmarks_num.THUMB_TIP]
        index_tip = hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[landmarks_num.MIDDLE_FINGER_TIP]

        # calc dist
        thumb_tip_arr = np.array([thumb_tip.x * 100, thumb_tip.y * 100, thumb_tip.z * 100])
        middle_tip_arr = np.array([middle_tip.x * 100, middle_tip.y * 100, middle_tip.z * 100])
        dist = np.linalg.norm(thumb_tip_arr - middle_tip_arr)

        # if state 0
        if self.state == FingerSnap.AVAILABLE_STATES[0]:
            # if index finger up, thumb and middle finger are close together
            if (thumb_tip.y > index_tip.y) and (dist < self.DISTANCE_THRESHOLD):
                self.state = FingerSnap.AVAILABLE_STATES[1]
        # if state 1
        elif self.state == FingerSnap.AVAILABLE_STATES[1]:
            # if thumb and middle finger are moves away from each other
            if (self.DISTANCE_THRESHOLD < dist) and (middle_tip.y > thumb_tip.y):
                if self.dist is None:
                    self.dist = dist
                    self.after_time = time.time()
                else:
                    if (self.dist < dist):
                        if (time.time() - self.after_time) > 0.2:
                            self.state = FingerSnap.AVAILABLE_STATES[2]
                    else:
                        self.state = FingerSnap.AVAILABLE_STATES[0]
        # if last state
        elif self.state == FingerSnap.AVAILABLE_STATES[2]:
            self.init()
            return True
        return False
    
    def handler(self):
        '''
        Default gesture handler

        (mac)
        '''
        import os
        shutdown = {
            0: 'sudo shutdown ',
            'sleep': '-s ',
            'time': 'now ',
        }
        time.sleep(1)
        os.system(shutdown[0] + shutdown['sleep'] + shutdown['time'])
        sys.exit(0)


# Examples
def example1():
    '''
    Example
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
                    finger1 = int(hand_landmarks.landmark[landmarks_num.THUMB_TIP].x * 100)
                    finger2 = int(hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP].x * 100)
                    dist = abs(finger1 - finger2)
                    cv2.putText(frame, 'f1=%d f2=%d dist=%d' % (finger1, finger2, dist), 
                                (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), thickness=3, lineType=cv2.LINE_AA)
                    draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()

def thanos_finger_snap():
    '''
    Thanos Finger Snap with webcam
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
    finger_snap_list = [FingerSnap(DISTANCE_THRESHOLD)] * max_num_hands
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    while cam.is_opened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            # get hand landmarks
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand_landmarker.get_result(img)
            if result.multi_handedness:
                for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                    # gesture
                    finger_snap = finger_snap_list[i]
                    if finger_snap.check(result.multi_handedness[i], hand_landmarks):
                        finger_snap.handler()
                    # draw landmarks
                    draw_landmarks(frame, hand_landmarks)
            else:
                for finger_snap in finger_snap_list:
                    finger_snap.init()
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()
