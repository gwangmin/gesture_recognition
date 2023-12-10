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
no multiprocessing
game title > game > game clear or game over로 구성
'''
print = sys.stdout.write

# initiation
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Gesture Bomber')
icon = pg.image.load('assets/spr_shield.png')
pg.display.set_icon(icon)
titleFont = pg.font.Font('assets/Ramche.ttf', 42)
stateFont = pg.font.Font('assets/Ramche.ttf', 30)

clock = pg.time.Clock()
prev_time = 0
FPS = 60            
count = 0

webcam = cv2.VideoCapture(0)
if not webcam.isOpened():
    print('Could not open webcam\n') 

'''
main function
'''

def main():
    while True:
        # Game
        showTitle()
        isClear = Game()
        # EndFile
        GameEnd(isClear)

def postHandEvent():
    global prev_time, webcam, px, py
    
    # hand tracking event get
    status, frame = webcam.read()
    current_time = time() - prev_time
    if (current_time > 1 / FPS) and status:
        recognition = api.gesture_recognizer(frame)
        gestureEvent = recognition[1][0]
        
        prev_time = time()
        if gestureEvent[0] == 1 and gestureEvent[1]['handedness'] == 'Left':
            print('OpenPalm\n')
            pg.event.post(pg.event.Event(OPENPALM_EVENT))
            
        if gestureEvent[0] == 3 and gestureEvent[1]['handedness'] == 'Right':
            # save position
            xpos = gestureEvent[1]['xyz'][0]
            ypos = gestureEvent[1]['xyz'][1]
            px = xpos * SCREEN_WIDTH
            py = ypos * SCREEN_HEIGHT
            '''
            new moving function
            '''
            print(f'Move: ({px}, {py})\n')
            pg.event.post(pg.event.Event(MOVE_EVENT))
            
        if gestureEvent[0] == 4 and gestureEvent[1]['handedness'] == 'Left':
            print('FingerSnap\n')
            pg.event.post(pg.event.Event(FINGERSNAP_EVENT))
            
        if gestureEvent[0] == 2 and gestureEvent[1]['handedness'] == 'Left':
            print('Pinch\n')
            pg.event.post(pg.event.Event(PINCH_EVENT))
            
def showTitle():
    print('showTitle\n')
    
    BACKGROUND_COLOR = pg.Color(80, 97, 125)
    screen.fill(BACKGROUND_COLOR)

    title = titleFont.render('GESTURE BOMBER', False, (0,0,0))
    rect = title.get_rect()
    rect.center = titlePos
    screen.blit(title, rect)

    pg.display.update()

    while True:
        postHandEvent()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                webcam.release()
                sys.exit()
            if event.type == PINCH_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_RIGHT):
                # start sound
                
                # function end
                del title
                pg.display.update()
                return
    
    
    
def Game():
    global count, FPS, clock, px, py, prev_time, webcam
    print('Game\n') 

    title = titleFont.render('GAME', False, (240,240,240))
    rect = title.get_rect()
    rect.center = titlePos
    
    state = stateFont.render('None', False, (240,240,240))
    sRect = state.get_rect()
    sRect.center = statePos
    
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
        postHandEvent()
        # game event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                webcam.release()
                sys.exit()
                
            if event.type == SPAWN_EVENT:
                print(f'spawn: {count}, {len(foeGroup)}\n')
                if count == 6:                
                    spawn(4, foeGroup)
                elif count == 12:
                    spawn(5, foeGroup)
                elif count < 12:
                    spawn(randint(1,3), foeGroup)
                count += 1
        
            if event.type == OPENPALM_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_DOWN):
                print('shield\n')
                player.useShield()
                
                state = stateFont.render('SHIELD', False, (240,240,240))
                sRect = state.get_rect()
                sRect.center = statePos
                screen.blit(state, sRect)
                player.draw(screen)
            if event.type == FINGERSNAP_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_UP):
                print('bomb\n')
                player.useBomb(fBulletGroup)                
                state = stateFont.render('BOMB', False, (240,240,240))
                sRect = state.get_rect()
                sRect.center = statePos
                screen.blit(state, sRect)
            if event.type == PINCH_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_RIGHT):
                pause = titleFont.render('PAUSE', False, (0,0,0))
                rect = pause.get_rect()
                rect.center = titlePos
                screen.fill((255,255,255))
                screen.blit(pause, rect)
                pg.display.update()
                paused = True
                while paused:
                    postHandEvent()
                    for event in pg.event.get():
                        if event.type == PINCH_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_RIGHT):
                            paused = False
                        if event.type == pg.QUIT:
                            pg.quit()
                            webcam.release()
                            sys.exit()
            '''
            if event.type == MOVE_EVENT:
                player.update(px, py)
            '''
            if event.type == F_FIRE_EVENT:
                for foe in foeGroup:
                    foe.fire(fBulletGroup)
            if event.type == P_FIRE_EVENT:
                player.fire(pBulletGroup)

        # collision check
        if pg.sprite.spritecollide(player, fBulletGroup, dokill=True, 
                                   collided=pg.sprite.collide_mask):
            player.loseLife()

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

        screen.fill((50,50,50))
        
        
        screen.blit(title, rect)
        screen.blit(state, sRect)
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

def GameEnd(isClear):
    print('Game End\n')
    if isClear:
        phrase = 'GAME CLEAR!'
    else:
        phrase = 'GAME OVER'

    screen.fill((10,10,10))
    title = titleFont.render(phrase, False, (240,240,240))
    rect = title.get_rect()
    rect.center = titlePos
    
    noticeStr = '다시 시작하시겠습니까?\n\n꼬집으면 재시작, 튕기면 종료됩니다.'
    notice = stateFont.render(noticeStr, False, (240,240,240))
    nRect = notice.get_rect()
    nRect.center = statePos
    
    screen.blit(title, rect)
    screen.blit(notice, nRect)
    
    pg.display.update()
            

    
    # transparent window and notice gesture; return to title or QUIT
    
    while webcam.isOpened():
        postHandEvent()
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == FINGERSNAP_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_UP):
                pg.quit()
                webcam.release()
                sys.exit()
            if event.type == PINCH_EVENT or (event.type == pg.KEYDOWN and event.key == pg.K_RIGHT):
                return
        

def spawn(n, group):
    if n == 1:
        Classes.Foe(groups=group, foeType='F', xpos=SCREEN_WIDTH * 0.1).add(group)
        Classes.Foe(groups=group, foeType='D', xpos=SCREEN_WIDTH * 0.2).add(group)
        #Foe(groups=group, foeType='F', xpos=firstMove(self)SCREEN_WIDTH * 0.1)
        Classes.Foe(groups=group, foeType='D', xpos=SCREEN_WIDTH * 0.8).add(group)
        Classes.Foe(groups=group, foeType='F', xpos=SCREEN_WIDTH * 0.9).add(group)
    if n == 2:
        Classes.Foe(groups=group, foeType='F', xpos=SCREEN_WIDTH * 0.1).add(group)
        Classes.Foe(groups=group, foeType='D', xpos=SCREEN_WIDTH * 0.3).add(group)
        Classes.Foe(groups=group, foeType='F', xpos=SCREEN_WIDTH * 0.5).add(group)
        Classes.Foe(groups=group, foeType='D', xpos=SCREEN_WIDTH * 0.7).add(group)
        Classes.Foe(groups=group, foeType='F', xpos=SCREEN_WIDTH * 0.9).add(group)
        
    if n == 3:
        Classes.Foe(groups=group, foeType='C', xpos=SCREEN_WIDTH * 0.3).add(group)
        Classes.Foe(groups=group, foeType='C', xpos=SCREEN_WIDTH * 0.4).add(group)
        Classes.Foe(groups=group, foeType='C', xpos=SCREEN_WIDTH * 0.5).add(group)
        Classes.Foe(groups=group, foeType='C', xpos=SCREEN_WIDTH * 0.6).add(group)
        Classes.Foe(groups=group, foeType='C', xpos=SCREEN_WIDTH * 0.7).add(group)
        
    if n == 4:
        Classes.MiniBoss(groups=group, xpos=SCREEN_WIDTH * 0.25).add(group)
        Classes.MiniBoss(groups=group, xpos=SCREEN_WIDTH * 0.75).add(group)
    if n == 5:
        Classes.Boss(groups=group).add(group)

if __name__ == '__main__':
    main()

