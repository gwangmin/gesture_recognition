'''
Main script
(This project's entry script)
'''


from pathlib import Path
from lib import hand_landmarks


# Settings
prj_dir = Path(__file__).resolve().parent # prj root dir


# Entry point
def main():
    '''
    Entry point
    '''
    hand_landmarks.playground()

if __name__ == '__main__':
    main()
