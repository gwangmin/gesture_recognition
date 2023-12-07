
import pygame as pg
from random import randint, choice
from time import time

import global_vars

'''
필요 클래스
'''

# item
# random generating 
class Item(pg.sprite.Sprite):
    speed = 7
    def __init__(self, groups, pos):
        super().__init__(self)
        self.itemName = choice(global_vars.ITEMS.keys())
        
        self.image = pg.image.load(global_vars.ITEMS[self.itemName]).convert_alpha()
        self.image = pg.transform.scale(self.image, global_vars.SCALED_SPRITE_SIZE, 24*4)
        # self.image.set_colorkey()
        
        self.rect = self.image.get_rect(center=pos)
    
    def update(self, args, kwargs):
        
        # collide

        # fall
        pass
    
    def draw(self, surf):
        surf.blit(self.image, self.rect)
        
    def fall(self):
        self.centery += self.speed
        

# Characters
class Player(pg.sprite.Sprite):
    life = 3            # life
    
    # test용 아이템
    bomb = 2
    savedShield = 2
    # test용 아이템
    shield = False
    power = 0
    
    def __init__(self, pos):
        super().__init__()
        self.lastTime = time()
        self.image = global_vars.SHIPS['PLAYER'].convert_alpha()
        self.image = pg.transform.scale(self.image, (global_vars.SCALED_SPRITE_SIZE, global_vars.SCALED_SPRITE_SIZE))
        self.firstpos = pos
        self.vpos = pg.math.Vector2(pos)

        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)
        
        self.movement = pg.math.Vector2(1, 1)
        self.speed = 7
    
    def update(self, surf):
        self.draw(surf)

    
    def draw(self, surf):
        surf.blit(self.image, self.rect)
        
    
    def getItem(self, itemName):
        if itemName == 'Powerup' and self.power < 4:
            self.power += 1
        if itemName == 'Lifeup':
            self.life += 1
        if itemName == '1timeshield':
            self.shield = True
            self.image = global_vars.SHIPS['SHIELDED'].convert_alpha()
            self.rect = self.image.get_rect()
            self.mask = pg.mask.from_surface(self.image)
        if itemName == 'Bomb':
            self.bomb += 1
        if itemName == 'Savedshield':
            self.savedShield += 1

    
    def fire(self, groups):
        if self.power == 0:
            Bullet(groups, 'SmallOne', self.pos+self.rect.width*0.4)
            Bullet(groups, 'SmallOne', self.pos-self.rect.width*0.4)
        if self.power == 1:
            Bullet(groups, 'SmallTwo', self.pos+self.rect.width*0.4)
            Bullet(groups, 'SmallTwo', self.pos-self.rect.width*0.4)
        if self.power == 2:
            Bullet(groups, 'BigOne', self.pos+self.rect.width*0.4)
            Bullet(groups, 'BigOne', self.pos-self.rect.width*0.4)
        if self.power == 3:
            Bullet(groups, 'BigOne', self.pos+self.rect.width*0.4)
            Bullet(groups, 'BigOne', self.pos-self.rect.width*0.4)
            Bullet(groups, 'SmallOne', self.pos+self.rect.width*0.4, angle=45)
            Bullet(groups, 'SmallOne', self.pos-self.rect.width*0.4, angle=-45)
            
        if self.power == 4:
            Bullet(groups, 'BigOne', self.pos+self.rect.width*0.4)
            Bullet(groups, 'BigOne', self.pos-self.rect.width*0.4)
            Bullet(groups, 'SmallOne', self.pos+self.rect.width*0.4, angle=45)
            Bullet(groups, 'SmallOne', self.pos-self.rect.width*0.4, angle=-45)
            
        
    def getLife(self):
        return self.life
    
    def loseLife(self):
        if self.shield:
            self.shield = False
            self.image = global_vars.SHIPS['PLAYER'].convert_alpha()
            self.rect = self.image.get_rect()
            self.mask = pg.mask.from_surface(self.image)
        else:
            self.life -= 1
            self.rect.center(self.firstpos)
            # when player dies something... happen
        
    def useBomb(self, bulletGroup):
        self.bomb -= 1
        bulletGroup.empty()
    
    def useShield(self):
        self.savedShield -= 1
        self.shield = True
        self.image = global_vars.SHIPS['SHIELDED'].convert_alpha()
        self.image = pg.transform.scale(self.image, (global_vars.SCALED_SPRITE_SIZE, global_vars.SCALED_SPRITE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)     
    
    
def firstMove(obj):
    for dt in range(0, global_vars.SCREEN_HEIGHT / 10, 10):
        obj.rect.centery += dt
    
    
class Foe(pg.sprite.Sprite):
    image = None
    rect = None
    
    def __init__(self, groups, foeType, xpos, life=1, speed=1):
        super().__init__(self)
        self.foeType = foeType
        
        # image load
        if self.foeType == 'F':
            self.image = global_vars.SHIPS['FGRADE'].convert_alpha()
        elif self.foeType == 'D':
            self.image = global_vars.SHIPS['DGRADE'].convert_alpha()
        elif self.foeType == 'C':
            self.image = global_vars.SHIPS['CGRADE'].convert_alpha()

        self.image = pg.transform.scale(self.image, (global_vars.SCALED_SPRITE_SIZE, global_vars.SCALED_SPRITE_SIZE))
        self.rect = self.image.get_rect(center=(xpos, 0))
        self.mask = pg.mask.from_surface(self.image)
        
        self.life = life
        self.speed = speed
        
        groups.add()
        firstMove(self)
                    
    def fire(self, groups):
        if self.foeType == 'F':
            Bullet(groups, self.rect.center, 'SmallOne', isFoe=True)
        elif self.foeType == 'D':
            Bullet(groups, self.rect.center, 'SmallOne', isFoe=True, angle=45)
            Bullet(groups, self.rect.center, 'SmallOne', isFoe=True, angle=-45)
        elif self.foeType == 'C':
            # 유도탄 함수
            Bullet(groups, self.rect.center, 'SmallOne', isFoe=True)
            
    def loseLife(self, damage):
        self.death()

    def death(self):
        # drop item, animate
        self.kill()
    
    def update(self, surf):
        self.draw(surf)
    
    def draw(self, surf):
        surf.blit(self.image, self.rect)

class MiniBoss(pg.sprite.Sprite):
    image = None
    rect = None
    y = 0

    def __init__(self, groups, xpos, life=5, speed=1):
        super().__init__()
        self.image = global_vars.SHIPS['MINIBOSS'].convert_alpha()
        self.image = pg.transform.scale(self.image, (global_vars.SCALED_SPRITE_SIZE, global_vars.SCALED_SPRITE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        
        self.life = life
        self.speed = speed
        
        self.rect.center = (xpos, 0)
        groups.add()
        firstMove(self)
    
    def move(self, dt):
        if randint(0, 2000) < 2:
            self.y_angle = True
            self.old_y = self.y
        if self.y_angle:
            if self.y < self.old_y + global_vars.SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else: self.y_angle = False
        else:
            if self.angle:
                self.x += self.speed * dt
                '''
                if self.x > config.window_size[0]-100:
                    self.angle = False
                '''
            else:
                self.x -= self.speed * dt
                if self.x < 5:
                    self.angle = True
                    
    def fire(self, groups):
        Bullet(groups, 'SmallOne', self.rect.center, isFoe=True)
        Bullet(groups, 'SmallOne', self.rect.center, isFoe=True, angle=45)
        Bullet(groups, 'SmallOne', self.rect.center, isFoe=True, angle=-45)
        
    def loseLife(self, damage):
        self.life -= damage
        if self.life < 1:
            self.death()

    def death(self):
        # drop item, animate
        
        self.kill()
    
    def update(self, surf):
        self.draw(surf)

    
    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Boss(pg.sprite.Sprite):
    image = None
    rect = None

    def __init__(self, groups, life=10, speed=0):
        super().__init__(self)
        self.image = global_vars.SHIPS['BOSS'].convert_alpha()
        self.image = pg.transform.scale(self.image, (global_vars.SCALED_SPRITE_SIZE, global_vars.SCALED_SPRITE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        
        self.rect.center = (global_vars.SCREEN_WIDTH * 0.5, 0)
        
        # global_vars.SHIPS{}
        self.life = life
        self.speed = speed
        
        groups.add()
        
        firstMove(self)
                    
    def fire(self, groups):
        Bullet(groups, 'BigOne', self.rect.center, isFoe=True)
        Bullet(groups, 'BigOne', self.rect.center, isFoe=True, angle=45)
        Bullet(groups, 'BigOne', self.rect.center, isFoe=True, angle=-45)

    def loseLife(self, damage):
        self.life -= damage
        if self.life < 1:
            self.death()

    def death(self):
        # drop item, animate
        
        self.kill()
    
    def update(self, surf):
        self.draw(surf)
    
    def draw(self, surf):
        surf.blit(self.image, self.rect)

# bullet
class Bullet(pg.sprite.Sprite):
    speed = 12
    
    def __init__(self, groups, kinds, pos, isFoe=False, angle=None):
        super().__init__(self)
        # 쏘는 객체의 위치, 벡터 값
        self.x, self.y = pos
        self.vpos = pg.math.Vector2(pos)
        
        self.isFoe = isFoe
        # angle; 방향 결정; default=None, left=negative angle, right=positive angle
        self.angle = angle

        if isFoe:
            self.image = global_vars.FBULLETS[kinds].convert_alpha()
            self.v_vm = pg.math.Vector2(0, 1)
        else:
            self.image = global_vars.PBULLETS[kinds].convert_alpha()
            self.v_vm = pg.math.Vector2(0, -1)
            
        self.image = pg.transform.scale(self.image, (global_vars.SPRITE_SIZE, global_vars.SPRITE_SIZE))
        if angle != None:
            self.v_vm = self.v_vm.rotate(angle=angle) * self.speed
            self.image = pg.transform.rotate(self.angle)
        
        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)
        groups.add()
        
    def update(self, surf):
        
        # collide
        
        # bullet move
        self.vpos += self.v_vm
        self.draw(surf)
            


    def draw(self, surf):
        surf.blit(self.image, self.rect)
        
def spawn(n, renderPlain):
    if n == 1:
        Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.1)
        Foe(groups=renderPlain, foeType='D', xpos=global_vars.SCREEN_WIDTH * 0.2)
        #Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.1)
        Foe(groups=renderPlain, foeType='D', xpos=global_vars.SCREEN_WIDTH * 0.8)
        Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.9)
    if n == 2:
        Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.1)
        Foe(groups=renderPlain, foeType='D', xpos=global_vars.SCREEN_WIDTH * 0.3)
        Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.5)
        Foe(groups=renderPlain, foeType='D', xpos=global_vars.SCREEN_WIDTH * 0.7)
        Foe(groups=renderPlain, foeType='F', xpos=global_vars.SCREEN_WIDTH * 0.9)
        
    if n == 3:
        Foe(groups=renderPlain, foeType='C', xpos=global_vars.SCREEN_WIDTH * 0.3)
        Foe(groups=renderPlain, foeType='C', xpos=global_vars.SCREEN_WIDTH * 0.4)
        Foe(groups=renderPlain, foeType='C', xpos=global_vars.SCREEN_WIDTH * 0.5)
        Foe(groups=renderPlain, foeType='C', xpos=global_vars.SCREEN_WIDTH * 0.6)
        Foe(groups=renderPlain, foeType='C', xpos=global_vars.SCREEN_WIDTH * 0.7)
        
    if n == 4:
        MiniBoss(groups=renderPlain, pos=global_vars.SCREEN_WIDTH * 0.25)
        MiniBoss(groups=renderPlain, pos=global_vars.SCREEN_WIDTH * 0.75)
    if n == 5:
        Boss(groups=renderPlain)
        