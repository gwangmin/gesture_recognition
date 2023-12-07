from multiprocessing import Process, Queue
import pygame, cv2, time

import global_vars
import gesture_recognizer.app as api

class Controller:
    def __init__(self, queue):
        self.eventQueue = queue
    
    def run(self):
        global px, py
        '''cv2 videocapture 생성'''
        webcam = cv2.VideoCapture(0)
        if not webcam.isOpened():
            print('Could not open webcam')
            if cv2.waitkey(1):
                # quit game
                exit()
            
        while webcam.isOpened():
            status, frame = webcam.read()
            
            if status:
                recognition = api.gesture_recognizer()
                gestureEvent = recognition[1][0]
                
                if gestureEvent == 1:
                    self.eventQueue.put(global_vars.OPENPALM_EVENT)
                elif gestureEvent == 2:
                    self.eventQueue.put(global_vars.PINCH_EVENT)
                elif gestureEvent == 3:
                    # save position
                    xpos = recognition[1]['xyz'][0]
                    ypos = recognition[1]['xyz'][1]
                    global_vars.px = xpos * global_vars.SCREEN_WIDTH
                    global_vars.py = ypos * global_vars.SCREEN_HEIGHT
                    
                    self.eventQueue.put(global_vars.MOVE_EVENT)
                elif gestureEvent == 4:
                    self.eventQueue.put(global_vars.FINGERSNAP_EVENT)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                webcam.release()
                break

'''
if __name__ == '__main__':
    q = Queue()
    p = Process(name='ControlProcess', target=Controller, args=(q, ))
    p.start()
    # game main이랑 q 동기화
    p.join()
'''