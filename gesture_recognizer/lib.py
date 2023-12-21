'''
Gesture recognizer basic module
'''

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks.python.components.containers import landmark as landmark_module
import cv2
import numpy as np
import requests
from typing import Callable, List, Dict, Tuple, Any, Optional


### detector & recognizer
landmarks_num = mp.solutions.hands.HandLandmark # landmark index

class HandLandmarker:
    '''
    [Deprecated]

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
    
    @classmethod
    def draw_landmarks(cls, rgb_img, one_hand_landmark_obj):
        '''
        Draw one hand landmarks.

        rgb_img: image
        one_hand_landmark_obj: one hand landmark obj.
        '''
        drawing_helper = mp.solutions.drawing_utils
        drawing_styles = mp.solutions.drawing_styles
        hands = mp.solutions.hands
        # draw
        drawing_helper.draw_landmarks(rgb_img, one_hand_landmark_obj, hands.HAND_CONNECTIONS,
                                      drawing_styles.get_default_hand_landmarks_style(),
                                      drawing_styles.get_default_hand_connections_style())

    @classmethod
    def plot_world_landmarks(cls, one_hand_world_landmark_obj):
        '''
        (accuracy is low)

        Plot one hand landmarks in world coord.

        one_hand_world_landmark_obj: one hand landmark obj in world coord.
        '''
        drawing_helper = mp.solutions.drawing_utils
        drawing_styles = mp.solutions.drawing_styles
        hands = mp.solutions.hands
        # draw
        drawing_helper.plot_landmarks(one_hand_world_landmark_obj, hands.HAND_CONNECTIONS,
                                      azimuth=5)
    
    def close(self):
        '''
        Release resources
        '''
        self.landmarker.close()

class GestureRecognizer:
    '''
    Gesture Recognizer using mp.
    https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer
    '''
    # latest model(.task) download url
    MODEL_DOWNLOAD_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task'
    # Mode
    IMAGE = vision.RunningMode.IMAGE
    VIDEO = vision.RunningMode.VIDEO
    LIVE_STREAM = vision.RunningMode.LIVE_STREAM
    # Basic gesture category_name
    NONE = 'None'
    CLOSED_FIST = 'Closed_Fist'
    OPEN_PALM = 'Open_Palm'
    POINTING_UP = 'Pointing_Up'
    THUMB_UP = 'Thumb_Up'
    THUMB_DOWN = 'Thumb_Down'
    VICTORY = 'Victory'
    ILOVEYOU = 'ILoveYou'

    def __init__(self, mode: vision.RunningMode = IMAGE, max_num_hands: int = 1,
                 result_callback: Optional[Callable[[vision.GestureRecognizerResult, mp.Image, int],None]] = None,
                 download_model: bool = True) -> None:
        '''
        Initializer.

        mode: Mode.
        max_num_hands: Maximum number of hands to detect.
        result_callback: The user-defined result callback for processing live stream data. 
            The result callback should only be specified when the mode is set to the live stream mode.
            # func(result: GestureRecognizerResult, input_image: mp.Image, timestamp_ms: int) -> None
        download_model: whether to download the latest model.
        '''
        # latest model download
        if download_model:
            self.download_latest_model()
        
        # create recognizer
        base_options = mp.tasks.BaseOptions(model_asset_path='gesture_recognizer.task')
        self.mode = mode
        if mode != self.LIVE_STREAM:
            options = vision.GestureRecognizerOptions(
                base_options=base_options,
                running_mode=mode,
                num_hands=max_num_hands,
            )
        else:
            if result_callback is None:
                raise Exception('result_callback required.')
            options = vision.GestureRecognizerOptions(
                base_options=base_options,
                running_mode=mode,
                num_hands=max_num_hands,
                result_callback=result_callback,
            )
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def download_latest_model(self) -> None:
        '''
        Download the latest gesture_recognizer model.
        '''
        resp = requests.get(self.MODEL_DOWNLOAD_URL)
        with open('gesture_recognizer.task', 'wb') as f:
            f.write(resp.content)

    def __parse_result(self, result: vision.GestureRecognizerResult) -> Any:
        '''
        Parse result.

        result: GestureRecognizerResult
                (https://developers.google.com/mediapipe/api/solutions/python/mp/tasks/vision/GestureRecognizerResult).

        return: parsed result.
        '''
        return result
    
    def get_result(self, rgb_img: np.ndarray, elapsed_timestamp_ms: Optional[int] = None) -> Any:
        '''
        Recognize gesture from rgb_img and return results.

        rgb_img: input rgb image.
        elapsed_timestamp_ms: elapsed time after start. in ms.

        return: GestureRecognizerResult
                (https://developers.google.com/mediapipe/api/solutions/python/mp/tasks/vision/GestureRecognizerResult).
        '''
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
        if self.mode == self.IMAGE:
            result = self.recognizer.recognize(mp_img)
        elif self.mode == self.VIDEO:
            result = self.recognizer.recognize_for_video(mp_img, elapsed_timestamp_ms)
        elif self.mode == self.LIVE_STREAM:
            # it's not guaranteed to have output per input image.
            self.recognizer.recognize_async(mp_img, elapsed_timestamp_ms)
            return None
        return self.__parse_result(result)

    @classmethod
    def draw_landmarks(cls, rgb_img: np.ndarray, one_hand_landmarks: List[landmark_module.NormalizedLandmark]) -> None:
        '''
        Draw one hand landmarks.

        rgb_img: image.
        one_hand_landmarks: one hand landmarks.
        '''
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in one_hand_landmarks
        ])
        HandLandmarker.draw_landmarks(rgb_img, hand_landmarks_proto)

    def close(self) -> None:
        '''
        Release resources
        '''
        self.recognizer.close()


### gestures
class OneHandGestureBase:
    '''
    Base class for One-Hand gesture recognition.
    [You should overrides all these methods]
    '''
    AVAILABLE_STATES = [None, 'others']
    def __init__(self) -> None:
        '''
        Default initializer.

        1. save gesture specific settings.
        2. call 'self.init()'.
        '''
        # ----- EXAMPLE CODE -----
        # save gesture specific settings
        self.settings = 'gesture specific settings'
        self.init()

    def init(self) -> None:
        '''
        Self initializing.

        initialize internal states.
        '''
        # ----- EXAMPLE CODE -----
        self.state = self.AVAILABLE_STATES[0]
    
    def check(self, handedness_name: str, hand_landmarks: List[landmark_module.NormalizedLandmark],
              info: Dict[str, Any]) -> bool:
        '''
        Check hand landmark detection result. return True, if gesture recognized.

        handedness_name: handedness display_name. 'Left' or 'Right'.
        hand_landmarks: one hand landmarks.
        info: other info dict.
                e.g. {'gesture_name': result.gestures[i][0].category_name}

        return: True, if gesture recognized.
        '''
        # ----- EXAMPLE CODE -----
        # if state 0
        if self.state == self.AVAILABLE_STATES[0]:
            pass
        # if last state
        elif self.state == self.AVAILABLE_STATES[-1]:
            self.init()
            return True
        return False
    
    def handler(self) -> Any:
        '''
        Default gesture handler.

        When gesture recognized, execute this method.
        '''
        raise NotImplementedError()

class TwoHandGestureManager:
    '''
    Manager for 2-Hand gesture recognition by 2 One-Hand gesture instance.
    '''
    def __init__(self, instances: Dict[str, OneHandGestureBase]) -> None:
        '''
        Initializer.

        instances: {handedness_name: OneHandGestureBase's_child_instance}.
                    e.g. {'Left': OneHandGestureBase's_child_instance, 'Right': OneHandGestureBase's_child_instance}.
        '''
        self.instances = instances
    
    def init(self, handedness_name: str) -> None:
        '''
        Call 'OneHandGestureBase.init' on specified instance.

        handedness_name: handedness display_name. 'Left' or 'Right'.
                            or 'all'.
        '''
        if handedness_name == 'all':
            for instance in self.instances.values():
                instance.init()
        else:
            self.instances[handedness_name].init()
    
    def check(self, handedness_name: str, hand_landmarks: List[landmark_module.NormalizedLandmark],
              info: Dict[str, Any]) -> bool:
        '''
        Call 'OneHandGestureBase.check' on specified instance.

        params and return: see 'OneHandGestureBase.check'.
        '''
        ret = self.instances[handedness_name].check(handedness_name, hand_landmarks, info)
        return ret

    def handler(self, handedness_name: str, *args: Any) -> Any:
        '''
        Call 'OneHandGestureBase.handler' on specified instance.
        
        handedness_name: handedness display_name. 'Left' or 'Right'.
        args: handler arguments.

        return: handler return.
        '''
        return self.instances[handedness_name].handler(*args)


### cv shortcuts
CV_R = (0, 0, 255)
CV_G = (0, 255, 0)
CV_B = (255, 0, 0)
CV_ORGS = [(10,30), (10,60), (10,90)]
def cv_draw_text(img: np.ndarray, text: str, org: Tuple[int, int], color: Tuple[int, int, int]):
    '''
    'cv2.putText' Shortcut func.

    img: image.
    text: string.
    org: Bottom-left corner of the text string in the image.
    color: bgr color. e.g. CV_R
    '''
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, 1, 
                color, thickness=3, lineType=cv2.LINE_AA)


### examples
def hand_landmarker_test():
    '''
    [Deprecated]

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
                    
                    HandLandmarker.draw_landmarks(frame, hand_landmarks)
            # show frame
            cv2.imshow('webcam', frame)
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    hand_landmarker.close()
    cam.release()
    cv2.destroyAllWindows()

def gesture_recognizer_test():
    '''
    Gesture recognizer test from webcam.
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

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # preprocessing
            frame = cv2.flip(frame, 1) # y-axis flip
            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # get results
            result = recognizer.get_result(rgb_img, timestamp_ms)
            # extract info
            if result.gestures:
                for i, one_hand_landmarks in enumerate(result.hand_landmarks):
                    handedness_str = f'Handedness: {result.handedness[i][0].display_name}'
                    cv_draw_text(frame, handedness_str, CV_ORGS[0], CV_R)
                    
                    gesture_category = f'Gesture: {result.gestures[i][0].category_name}'
                    cv_draw_text(frame, gesture_category, CV_ORGS[1], CV_G)
                    
                    index_tip = one_hand_landmarks[landmarks_num.INDEX_FINGER_TIP]
                    index_tip_str = f'INDEX_FINGER_TIP: {int(index_tip.x*100)}, {int(index_tip.y*100)}, {int(index_tip.z*100)}'
                    cv_draw_text(frame, index_tip_str, CV_ORGS[2], CV_B)
                    
                    GestureRecognizer.draw_landmarks(frame, one_hand_landmarks)
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
    gesture_recognizer_test()
