# gesture_recognition
gesture recognition library using mediapipe.

# Requirements
- python 3.9
- mediapipe 0.9.1.0
- numpy 1.26.1
- opencv-python 4.8.1
- requests 2.31.0

# How to run example script
'python -m gesture_recognizer.examples.gesture_test' in gesture_recognition(prj root) dir.

# How to implements your own gesture
1. add .py file into gesture_recognizer/gestures dir.
2. extends gesture_recognizer.lib.gesture_templates.OneHandGestureBase and overrides all methods(see code guide in OneHandGestureBase source code).
3. write test func(example: victory func in victory.py).

# todo
