'''
Hand landmarks detection
'''


import mediapipe as mp
import cv2
import numpy as np


### hand landmark
landmarks_num = mp.solutions.hands.HandLandmark # landmark index

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

    def __parse_result(self, result):
        '''
        Parse detection result
        '''
        return result

    def get_result(self, rgb_img):
        '''
        Process rgb_img and return result
        
        return:
            A NamedTuple object with the following fields:
            1) a "multi_hand_landmarks" field that contains the hand landmarks on
                each detected hand. [0,1]
            2) a "multi_hand_world_landmarks" field that contains the hand landmarks
                on each detected hand in real-world 3D coordinates that are in meters
                with the origin at the hand's approximate geometric center.
            3) a "multi_handedness" field that contains the handedness (left v.s.
                right hand) of the detected hand.
        '''
        result = self.landmarker.process(rgb_img)
        return self.__parse_result(result)
    
    def close(self):
        '''
        Release resources
        '''
        self.landmarker.close()


### Drawing & Plotting
drawing_helper = mp.solutions.drawing_utils
drawing_styles = mp.solutions.drawing_styles

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


### gestures
class OneHandGestureBase:
    '''
    Base class for one hand gesture recognition
    '''
    AVAILABLE_STATES = [None, 'others']
    def __init__(self) -> None:
        '''
        Default initializer

        1. save gesture specific settings.
        2. call self.init()
        '''
        # save gesture specific settings
        self.settings = 'gesture specific settings'
        self.init()

    def init(self):
        '''
        Self initializing
        '''
        raise NotImplementedError()
    
    def check(self, handedness, hand_landmarks):
        '''
        Check hand landmark detection result. return True, if gesture recognized.

        handedness: one handedness
        hand_landmarks: one hand landmarks
        '''
        raise NotImplementedError()
    
    def handler(self):
        '''
        Default gesture handler

        When gesture recognized, execute this method.
        '''
        raise NotImplementedError()

class OneHandGestureManager:
    '''
    Manager for Multi-Hand gesture recognition using One-Hand gesture class
    '''
    def __init__(self, one_hand_gesture_list) -> None:
        '''
        Initializer

        one_hand_gesture_list: [OneHandGestureBase's child instance] * max_num_hands
        '''
        self.instance_list = one_hand_gesture_list
    
    def init(self, idx):
        '''
        Call 'init' on specified instance

        idx: index or 'all'
        '''
        if idx == 'all':
            for instance in self.instance_list:
                instance.init()
        else:
            self.instance_list[idx].init()
    
    def check(self, idx, result):
        '''
        Call 'check' on specified instance

        idx: index
        '''
        handedness = result.multi_handedness[idx]
        hand_landmarks = result.multi_hand_landmarks[idx]
        ret = self.instance_list[idx].check(handedness, hand_landmarks)
        return ret

    def handler(self, idx):
        '''
        Call 'handler' on specified instance
        
        idx: index
        '''
        self.instance_list[idx].handler()


### examples
def playground():
    '''
    Hand landmark detection test from webcam
    '''
    hand_landmarker = HandLandmarker(max_num_hands=2,
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
                    draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()

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
                    thumb_tip = hand_landmarks.landmark[landmarks_num.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[landmarks_num.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[landmarks_num.MIDDLE_FINGER_TIP]

                    thumb_tip_arr = np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z])
                    index_tip_arr = np.array([index_tip.x, index_tip.y, index_tip.z])
                    middle_tip_arr = np.array([middle_tip.x, middle_tip.y, middle_tip.z])
                    dist = np.linalg.norm(thumb_tip_arr - middle_tip_arr)
                    
                    cv2.putText(frame, 
                                f'thumb: {thumb_tip.x*100}, index: {index_tip.x*100}, dist: {dist*100}', 
                                (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 
                                thickness=3, lineType=cv2.LINE_AA)
                    draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    example1()
