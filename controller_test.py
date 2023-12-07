import sys, cv2
from time import time
from multiprocessing import Process, Queue
from random import randint

import pygame as pg
import Activity, Classes
from global_vars import *

import gesture_recognizer.app as api


'''
game test; 
서드파티 GUI api에 오류가 있어 제외;
게임 파트만 분리한 파일입니다
game title > game > game clear or game over로 구성
'''

def delta_time(last_time):
    dt = time() - last_time
    dt *= FPS
    last_time = time()
    return dt, last_time





'''
main function
'''
'''
# initiation
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Gesture Bomber')
#pg.display.set_icon('assets/spr_shield.png')
'''
clock = pg.time.Clock()
prev_time = 0
FPS = 30

def controller(q):
    global px, py, prev_time
    print('Controller run started')
    '''cv2 videocapture 생성'''
    webcam = cv2.VideoCapture(0)
    if not webcam.isOpened():
        print('Could not open webcam')
            
    while webcam.isOpened():
        status, frame = webcam.read()

        current_time = time() - prev_time
        
        if (current_time > 1 / FPS) and status :
            recognition = api.gesture_recognizer(frame)
            gestureEvent = recognition[1][0]
            
            prev_time = time()
                
            if gestureEvent == 1:
                q.put(OPENPALM_EVENT)
            elif gestureEvent == 2:
                q.put(PINCH_EVENT)
            elif gestureEvent == 3:
                    # save position
                xpos = recognition[1]['xyz'][0]
                ypos = recognition[1]['xyz'][1]
                px = xpos * SCREEN_WIDTH
                py = ypos * SCREEN_HEIGHT
                    
                q.put(MOVE_EVENT)
            elif gestureEvent == 4:
                q.put(FINGERSNAP_EVENT)
        
        if cv2.waitKey(1) and 0xFF == ord('q'):
            #webcam.release()
            #cv2.destroyAllWindows()
            break
        if q.qsize() != 0:
            print(q.get())

if __name__ == '__main__':
    q = Queue()
    print('Process making')
    controller(q)
    #p = Process(name='ControlProcess', target=controller, args=(q, ))
    print('Process start')
    #p.start()
    # game main이랑 q 동기화
    #main(q)

