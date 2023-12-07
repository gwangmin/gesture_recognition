import sys
from time import time
import pygame as pg
import pygame_gui as gui

import Activity, Classes, Controller
from global_vars import *

'''
main game class; define UI
'''

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Gesture Bomber')
# pg.display.set_icon()

clock = pg.time.Clock()
FPS = 30
# background setting
BACKGROUND_COLOR = pg.Color(80, 97, 125)
screen.fill(BACKGROUND_COLOR)

manager = gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

class Game():
    level = 1
    
    def __init__(self, screen=screen):
        super().__init__()
        self.lastTime = time()
                
    def start(self):
        pass
        
    def update(self, surf=screen):
        pass
    
    def getEvent(self, event):
        pass
        
    def draw(self, surf=screen):
        
        # item 및 pause 키 표시용 상위 hud
        
        # game
        pass


class GameRunner(object):
    def __init__(self, screen, manager, states, start_state):
        self.screen = screen
        self.manager = manager
        self.states = states
        self.stateName = start_state
        self.state = self.states[self.stateName]
        self.time_delta = clock.tick(FPS) / 1000

        self.state.start()
        self.run()
    
    def run(self):
        running = True
        
        while running:
            self.getEvents()
            self.update()
            self.draw()
        
    def getEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            ''' get event from controller'''  
            self.state.getEvent(event)
            
    def update(self):
        self.state.update()
        if self.state.done:
            self.nextState()
    
    def nextState(self, stateName):
        nextState = stateName
        self.state.done = False
        self.stateName = nextState
        self.state = self.states[self.stateName]
        self.state.start()
    
    def quit(self):
        pg.quit()
        # save?
        sys.exit()
        
    def draw(self):
        # pygame.display.set_icon(pygame.image.load('assets/player_idle1.png'))
        
        clock.tick(FPS)

        self.state.draw(self.screen, self.manager)
        pg.display.update()
        

if __name__ == '__main__':
    states = {
        'Title':    Activity.Title(),
        'Game':     Activity.Game(),
        'Rank':     Activity.Rank(),
        'Pause':    Activity.Pause(),
        'Setting':  Activity.Setting(),
        'Sync':     Activity.Sync(),
        'GameEnd':  Activity.GameEnd()
    }
    game = GameRunner(screen, manager, states, 'Title')
