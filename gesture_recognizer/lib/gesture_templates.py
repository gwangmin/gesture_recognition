'''
Gesture templates
for easier implementations
for consistent api
'''

from mediapipe.tasks.python.components.containers import landmark as landmark_module
from typing import List, Dict, Any


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
