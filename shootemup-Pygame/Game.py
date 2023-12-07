from Classes import *
from states.Menu import Menu
from states.Pause import *
from states.GameState import GameState
from states.Options import Options
from states.DeathScreen import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *

pygame.init()
clock = pygame.time.Clock()
if config.set_fullscreen:   screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN, vsync=True)
else:                       screen = pygame.display.set_mode(config.window_size, vsync=True)

last_time = time()


class Game(GameState):
    level = 1
    def __init__(self, screen=screen):
        super().__init__()
        self.player = Player((config.window_size[0] / 2, (config.window_size[1] / 2)+150))
        self.background_fall = Fall(300)
        self.bullets = Bullet(self.player.rect[0] + SPRITE_SIZE, self.player.rect[1] + SPRITE_SIZE / 2, 5)
        self.next_state = "Pause"
        self.last_time = last_time
        self.level = 1
        self.level_done = False

    def start(self):
        if not self.level_done:
            Enemy1.spawn_enemy(self.level * 5)
            self.level_done = True

    def get_event(self, event):
        if event.type == KEYDOWN:
            self.player.get_input(event)

            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            self.player.get_input_keyup(event)

    def update(self, surf=screen):
        dt, self.last_time = delta_time(self.last_time)
        self.bullets.update(dt, surf)
        self.player.update(dt, self.last_time)
        self.background_fall.update()
        if Enemy1.instancelist is not None: [instance.update(dt, surf) for instance in Enemy1.instancelist]
        if not len(Enemy1.instancelist):
            self.level += 1
            Enemy1.spawn_enemy(self.level * 5)
            self.level_done = True
        if not Player.getLife(self.player):
            self.next_state = "Death"
            Player.setLife(self.player, 3)
            self.done = True

    def draw(self, surf=screen):
        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)
        self.background_fall.draw(surf)
        self.player.draw(surf)
        text(f'Level {self.level}', config.window_size[0] - 50, config.window_size[1] - 30, original_font=False)
        if config.show_fps:
            text(f'FPS: {(int(clock.get_fps()))}', 50, 30, original_font=False)


class GameRunner(object):
    def __init__(self, screen, states, start_state):
        self.screen = screen
        self.states = states
        self.start_state = start_state
        self.state = self.states[self.start_state]

        self.state.start()
        self.run()

    def run(self):
        running = True
        while running:
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            self.state.get_event(event)

    def update(self):
        self.state.update()
        if self.state.done:
            self.next_state()

    def next_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.start()

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw(self):

        pygame.display.set_icon(pygame.image.load('assets/player_idle1.png'))
        pygame.display.set_caption(f'Shoot \'em Up - Pygame. FPS: {int(clock.get_fps())}')
        clock.tick(FRAME_RATE)
        pygame.display.update()
        self.state.draw(self.screen)


player = None
# import multiprocessing as mp
# q = mp.Queue()


def main():
    global player
    states = {
        "Menu":     Menu(),
        "Game":     Game(),
        "Pause":    Pause(),
        "Exit":     Exit(),
        "Options":  Options(),
        "Death":    Death()
    }
    game = GameRunner(screen, states, "Menu")
    player = states['Game'].player
    # q.put(game)

import pyautogui
import gesture_recognizer.app as api
import cv2
# install mediapipe, requests, pyautogui
x = 0
y = 0


def a():
    global x, y
    cam = cv2.VideoCapture(0)
    # cv2.namedWindow('webcam', cv2.WINDOW_AUTOSIZE) # this window size cannot change, automatically fit the img

    while cam.isOpened():
        success, frame = cam.read() # get frame from cam
        if success:
            # func call
            result = api.gesture_recognizer(frame)

            for gesture in result[1]:
                if gesture[0] == 0:
                    # none
                    continue
                elif gesture[1]['handedness'] == 'Left':
                    if gesture[0] == 3:
                        # left hand - fist move
                        new_x = gesture[1]['xyz'][0]
                        new_y = gesture[1]['xyz'][1]
                        dx = new_x - x
                        dy = new_y - y
                        if dx < 0:
                            player.moving_left = True
                            pyautogui.press('left')
                            print('L')
                            # text = 'a'
                            # cv2.putText(result[0], text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                            #                     (0,0,255), thickness=3, lineType=cv2.LINE_AA)
                        elif 0 < dx:
                            pyautogui.press('right')
                        if dy < 0:
                            pyautogui.press('up')
                        elif 0 < dy:
                            pyautogui.press('down')
                        x = new_x
                        y = new_y
            
            # show frame
            # cv2.imshow('webcam', result[0])
            if cv2.waitKey(delay=1) == ord('q'):
                break
    # exit
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # import a
    # p2 = mp.Process(target=a.main, args=(q,))
    # p2.start()
    main()