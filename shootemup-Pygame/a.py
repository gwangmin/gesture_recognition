import pyautogui
import gesture_recognizer.app as api
import cv2
import time
# install mediapipe, requests, pyautogui
x = 0
y = 0


def main():
    global x, y
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # func call
            result = api.gesture_recognizer(frame)

            for gesture in result[1]:
                # none
                if gesture[0] == 0:
                    continue
                # Left hand
                elif gesture[1]['handedness'] == 'Left':
                    pass
                # Right hand
                elif gesture[1]['handedness'] == 'Right':
                    # fist move
                    if gesture[0] == 3:
                        new_x = gesture[1]['xyz'][0] * 100
                        new_y = gesture[1]['xyz'][1] * 100
                        print(f'new_x, new_y: ({new_x}, {new_y})')
                        dx = new_x - x
                        dy = new_y - y
                        print(f'dx, dy: ({dx}, {dy})')
                        unit = 3
                        if dx < -unit:
                            pyautogui.keyDown('a')
                            pyautogui.keyUp('a')
                        elif unit < dx:
                            pyautogui.keyDown('d')
                            pyautogui.keyUp('d')
                        if dy < -unit:
                            pyautogui.keyDown('w')
                            pyautogui.keyUp('w')
                        elif unit < dy:
                            pyautogui.keyDown('s')
                            pyautogui.keyUp('s')
                        x = new_x
                        y = new_y
                    # click
                    # elif gesture[0] == 2:
                    #     pyautogui.keyDown()
                    #     pyautogui.keyUp()

            # show frame
            # cv2.imshow('webcam', result[0])
            if cv2.waitKey(delay=300) == ord('q'):
                break
    # exit
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()