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
def spawn(n, renderPlain):

    if n == 1:
        Classes.Foe(groups=renderPlain, foeType='F', xpos=SCREEN_WIDTH * 0.1).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='D', xpos=SCREEN_WIDTH * 0.2).add(renderPlain)
        #Foe(groups=renderPlain, foeType='F', xpos=firstMove(self)SCREEN_WIDTH * 0.1)
        Classes.Foe(groups=renderPlain, foeType='D', xpos=SCREEN_WIDTH * 0.8).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='F', xpos=SCREEN_WIDTH * 0.9).add(renderPlain)
    if n == 2:
        Classes.Foe(groups=renderPlain, foeType='F', xpos=SCREEN_WIDTH * 0.1).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='D', xpos=SCREEN_WIDTH * 0.3).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='F', xpos=SCREEN_WIDTH * 0.5).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='D', xpos=SCREEN_WIDTH * 0.7).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='F', xpos=SCREEN_WIDTH * 0.9).add(renderPlain)
        
    if n == 3:
        Classes.Foe(groups=renderPlain, foeType='C', xpos=SCREEN_WIDTH * 0.3).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='C', xpos=SCREEN_WIDTH * 0.4).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='C', xpos=SCREEN_WIDTH * 0.5).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='C', xpos=SCREEN_WIDTH * 0.6).add(renderPlain)
        Classes.Foe(groups=renderPlain, foeType='C', xpos=SCREEN_WIDTH * 0.7).add(renderPlain)
        
    if n == 4:
        Classes.MiniBoss(groups=renderPlain, xpos=SCREEN_WIDTH * 0.25).add(renderPlain)
        Classes.MiniBoss(groups=renderPlain, xpos=SCREEN_WIDTH * 0.75).add(renderPlain)
    if n == 5:
        Classes.Boss(groups=renderPlain).add(renderPlain)
    

# initiation
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Gesture Bomber')
#pg.display.set_icon('assets/spr_shield.png')
clock = pg.time.Clock()
prev_time = 0
FPS = 60

def main(queue):
    # background setting
    BACKGROUND_COLOR = pg.Color(80, 97, 125)
    screen.fill(BACKGROUND_COLOR)
    pg.display.update()
    lastTime = time()
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
        input()

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
            
count = 0
prev_time = 0
    
def Game(q):
    global count, FPS, clock, px, py, prev_time
    print('Game')
    screen.fill((40, 200, 200))
    
    webcam = cv2.VideoCapture(0)
    if not webcam.isOpened():
        print('Could not open webcam')    

    sysfont = pg.font.SysFont('consolas', 30)
    title = sysfont.render('Gaming', True, (0,0,0))
    rect = pg.rect.Rect(300, 300, 300, 300)
    rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    screen.blit(title, rect)

    count = 0
        
    itemGroup = pg.sprite.Group()
    foeGroup = pg.sprite.Group()
    pBulletGroup = pg.sprite.Group()
    fBulletGroup = pg.sprite.Group()
    
    player = Classes.Player(pos=(px, py))
    
    spawnDelay = 1000 * 5     # spawn delay
    pg.time.set_timer(SPAWN_EVENT, spawnDelay)
    pFireDelay = int(1000 * 0.8)
    fFireDelay = 1000 * 1
    pg.time.set_timer(F_FIRE_EVENT, pFireDelay)
    pg.time.set_timer(P_FIRE_EVENT, fFireDelay)

    
    while webcam.isOpened():
        # hand tracking event get
        status, frame = webcam.read()
        current_time = time() - prev_time
        if (current_time > 1 / FPS) and status:
            recognition = api.gesture_recognizer(frame)
            gestureEvent = recognition[1][0]
            
            prev_time = time()
                
            if gestureEvent[0] == 1:
                pg.event.post(pg.event.Event(OPENPALM_EVENT))
            elif gestureEvent[0] == 2:
                pg.event.post(pg.event.Event(PINCH_EVENT))
            elif gestureEvent[0] == 3:
                # save position
                xpos = gestureEvent[1]['xyz'][0]
                ypos = gestureEvent[1]['xyz'][1]
                px = xpos * SCREEN_WIDTH
                py = ypos * SCREEN_HEIGHT
                print(px, py)

                pg.event.post(pg.event.Event(MOVE_EVENT))
            elif gestureEvent[0] == 4:
                pg.event.post(pg.event.Event(FINGERSNAP_EVENT))

        # game event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
                
            if event.type == SPAWN_EVENT:
                print(f'spawn: {count}, {len(foeGroup)}')
                if count == 6:                
                    spawn(4, foeGroup)
                elif count == 12:
                    spawn(5, foeGroup)
                elif count < 12:
                    spawn(randint(1,3), foeGroup)
                count += 1
        
            if event.type == OPENPALM_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_DOWN):
                print('shield')
                player.useShield()
                player.draw(screen)
            if event.type == FINGERSNAP_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_UP):
                print('bomb')
                player.useBomb(fBulletGroup)
            if event.type == PINCH_EVENT:
                print('pinch')
            
            if event.type == MOVE_EVENT:
                print('move')
                player.update(px, py)
            if event.type == F_FIRE_EVENT:
                for foe in foeGroup:
                    foe.fire(fBulletGroup)
            if event.type == P_FIRE_EVENT:
                player.fire(pBulletGroup)

        # collision check
        if pg.sprite.spritecollide(player, fBulletGroup, dokill=True, 
                                   collided=pg.sprite.collide_mask):
            player.loseLife()
            print(player.getLife())

        if pg.sprite.spritecollide(player, foeGroup, dokill=False, 
                                   collided=pg.sprite.collide_mask):
            player.loseLife()
                
        foeDict = pg.sprite.groupcollide(pBulletGroup, foeGroup, dokilla=True, dokillb=False, collided=pg.sprite.collide_mask)
        for bullet in foeDict:
            for foe in foeDict[bullet]: 
                foe.loseLife(1)
                if foe.life < 1:
                    foe.death(itemGroup)
                
        # item handling
        item = pg.sprite.spritecollide(player, itemGroup, dokill=True, collided=pg.sprite.collide_mask)
        for i in item:
            player.getItem(i.itemName)
                
        player.update(px, py)            
        foeGroup.update()
        pBulletGroup.update()
        fBulletGroup.update()
        itemGroup.update()

        screen.fill((40, 200, 200))       
        player.draw(screen)
        foeGroup.draw(screen)
        pBulletGroup.draw(screen)
        fBulletGroup.draw(screen)
        itemGroup.draw(screen)
    
        pg.display.update()
        pg.display.flip()
        clock.tick(FPS)

        # game over or game clear
        if player.getLife() == 0:
            return False
        
        if len(foeGroup) < 1 and count > 12:
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
            sys.exit()
        if event.type == PINCH_EVENT:
            return
    
    pg.display.update()
            

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
            sys.exit()
        if event.type == PINCH_EVENT:
            return
        
    pg.display.update()

if __name__ == '__main__':
    q = Queue()
    # game main이랑 q 동기화
    main(q)

