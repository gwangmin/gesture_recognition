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

# initiation
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Gesture Bomber')
#pg.display.set_icon('assets/spr_shield.png')
prev_time = 0
FPS = 30

def controller(q):
    global px, py
    print('Controller run started')
    '''cv2 videocapture 생성'''
    webcam = cv2.VideoCapture(0)
    if not webcam.isOpened():
        print('Could not open webcam')
            
    while webcam.isOpened():
        status, frame = webcam.read()

        current_time = time() - prev_time
        
        if (current_time > 1 / FPS) and status :
            recognition = api.gesture_recognizer()
            gestureEvent = recognition[1][0]
                
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




def main(queue):
    clock = pg.time.Clock()
    # background setting
    BACKGROUND_COLOR = pg.Color(80, 97, 125)
    screen.fill(BACKGROUND_COLOR)
    pg.display.update()
    lastTime = time()
    
    clock.tick(FPS)
    # Title
    showTitle(queue)
    while True:
        # Game
        isClear = Game(queue)
        # EndFile
        if isClear:
            gameClear(queue)
        else:
            gameOver(queue)

def showTitle(q):

    print('showTitle')
    # title text
    sysfont = pg.font.SysFont('consolas', 30)
    title = sysfont.render('Gesture Bomber', True, (0,0,0))
    rect = pg.rect.Rect(300, 300, 300, 300)
    rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    screen.blit(title, rect)

    pg.display.update()

    while True:
        if q.qsize() != 0:
            e = q.get()
            pg.event.post(pg.event.Event(e))
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                return
            if event.type == PINCH_EVENT or event.type == MOVE_EVENT:
                # start sound
                
                # function end
                del title
                pg.display.update()
                return
            

    
def Game(q):
    print('Game')
    screen.fill((40, 200, 200))

    sysfont = pg.font.SysFont('consolas', 30)
    title = sysfont.render('Gaming', True, (0,0,0))
    rect = pg.rect.Rect(300, 300, 300, 300)
    rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    screen.blit(title, rect)

    count = 0
        
    playerGroup = pg.sprite.RenderPlain()
    foeGroup = pg.sprite.RenderPlain()
    pBulletGroup = pg.sprite.RenderPlain()
    fBulletGroup = pg.sprite.RenderPlain()
    
    player = Classes.Player(pos=(px, py))
    
    spawnDelay = 1000 * 15     # spawn delay
    pg.time.set_timer(SPAWN_EVENT, spawnDelay)
    
    while True:
        # hand tracking event get
        if q.qsize() != 0:
            pg.event.post(q.get())
        
        # game event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.quit()
                
            if event.type == SPAWN_EVENT:
                if count == 6:                
                    Classes.spawn(4, foeGroup)
                elif count == 12:
                    Classes.spawn(5, foeGroup)
                elif count < 12:
                    Classes.spawn(randint(1,3), foeGroup)
                count += 1
        
            if event.type == OPENPALM_EVENT:
                player.useShield()
            if event.type == FINGERSNAP_EVENT:
                player.useBomb(fBulletGroup)
            
            if event.type == MOVE_EVENT:
                player.movement = pg.math.Vector2(px, py).normalize()
                player.vpos += player.movement * player.speed
                player.rect.center = (round(player.vpos.x), round(player.vpos.y))

        # collision check
        if pg.sprite.spritecollide(player, fBulletGroup, dokill=False, 
                                   collided=pg.sprite.collide_mask):
            player.loseLife()

        if pg.sprite.spritecollide(player, foeGroup, dokill=False, 
                                   collided=pg.sprite.collide_mask):
            player.loseLife()
                
        foeDict = pg.sprite.groupcollide(foeGroup, pBulletGroup, dokilla=False, dokillb=True, collided=pg.sprite.collide_mask)
        for i in foeDict.keys():
            foeDict[i].loseLife()
                
        # item handling
            #if pg.sprite.collide_mask(self.player, item)

        pBulletGroup.draw(screen)
        fBulletGroup.draw(screen)
        player.draw(screen)
    
        pBulletGroup.update(screen)
        fBulletGroup.update(screen)
        player.update(screen)
        
        pg.display.flip()

        # game over or game clear
        if player.getLife() == 0:
            return False
        
        if len(foeGroup) < 1:
            return True


def gameOver(q):
    print('GameOver')

    screen.fill((200, 40, 200))
    sysfont = pg.font.SysFont('consolas', 30)
    title = sysfont.render('Game Over', True, (0,0,0))
    rect = pg.rect.Rect(300, 300, 300, 300)
    rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    screen.blit(title, rect)

    
    # gameover text
        # hand tracking event get
    if q.qsize() != 0:
        pg.event.post(q.get())    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.quit()
        if event.type == PINCH_EVENT:
            return
            

def gameClear(q):
    # gameclear text
    print('GameClear')

    screen.fill((200, 40, 200))
    sysfont = pg.font.SysFont('consolas', 30)
    title = sysfont.render('Game Clear', True, (0,0,0))
    rect = pg.rect.Rect(300, 300, 300, 300)
    rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    screen.blit(title, rect)

    
    if q.qsize() != 0:
        pg.event.post(q.get()) 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.quit()
        if event.type == PINCH_EVENT:
            return
        

if __name__ == '__main__':
    q = Queue()
    print('Process making')
    p = Process(name='ControlProcess', target=controller, args=(q, ))
    print('Process start')
    p.start()
    # game main이랑 q 동기화
    main(q)

