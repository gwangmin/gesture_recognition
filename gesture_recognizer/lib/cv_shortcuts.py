'''
opencv shortcuts
'''

import cv2
import numpy as np
from typing import Tuple


# color
CV_R = (0, 0, 255)
CV_G = (0, 255, 0)
CV_B = (255, 0, 0)
# org point
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
