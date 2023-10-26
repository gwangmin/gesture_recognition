'''
Hand landmarks detection
turn the page:
    한 손을 휘젓는 것으로 화면을 이전/다음으로 넘기는 제스처    
    
'''

import sys
import time
import cv2
import numpy as np

from lib import OneHandGestureBase
from lib import OneHandGestureManager
from lib import HandLandmarker
from lib import landmarks_num
from lib import draw_landmarks

class HandSwing(OneHandGestureBase):
    '''
    This class represents Finger Snap Gesture

    states:
        None - Nothing detected
        before - prepare finger snap
        after - after snap sounds
    '''
    AVAILABLE_STATES = [None, 'before', 'after']
    def __init__(self, DISTANCE_THRESHOLD=4.0, KEEP_DURATION=0.05) -> None:
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
        self.state = HandSwing.AVAILABLE_STATES[0]
        # init landmarks
        
    def check(self):
        '''
        check the gesture
        '''
        
        '''
        memo:
            손가락끼리의 상대적 위치보다는 손 전체의 위치
            카메라에 보이는 landmark: 8, 12, 16 (tips)
            INDEX 8, 12, 16의 x좌표의 차; 한쪽 끝에서 다른 쪽 끝으로 움직이면 check=True
            (단순히 손이 흔들리는 것과는 구분되어야 하므로 동작을 크게 정의할 것)
            동작의 방향(부호)에 따라 action이 달라질 수 있음
            
        '''
        pass
    
    
    def handler(self):
        '''
        link gesture & action (turn the page)
        '''
        pass
    
def hand_swing():
    pass

