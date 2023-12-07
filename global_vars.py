import pygame as pg

# 상수

'''
0: nothing
1: 주먹펴기
2: 꼬집기
3: 움직임
4: 핑거스냅
'''
# pg.event.Event()

OPENPALM_EVENT = pg.USEREVENT + 1
PINCH_EVENT = pg.USEREVENT + 2
MOVE_EVENT = pg.USEREVENT + 3
FINGERSNAP_EVENT = pg.USEREVENT + 4

SPAWN_EVENT = pg.USEREVENT + 5
F_FIRE_EVENT = pg.USEREVENT + 6
P_FIRE_EVENT = pg.USEREVENT + 7

CONTROLS = {
    'UP':       [pg.K_w, pg.K_UP],
    'DOWN':     [pg.K_s, pg.K_DOWN],
    'RIGHT':    [pg.K_d, pg.K_RIGHT],
    'LEFT':     [pg.K_a, pg.K_LEFT],
    'START':    [pg.K_RETURN],
    'ESC':      [pg.K_ESCAPE],
    'OPENPALM': [OPENPALM_EVENT],
    'PINCH':    [PINCH_EVENT],
    'MOVE':     [MOVE_EVENT],
    'FINGERSNAP': [FINGERSNAP_EVENT]
}

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# gui values
BUTTON_WIDTH = SCREEN_WIDTH * 0.2
BUTTON_HEIGHT = SCREEN_WIDTH * 0.2

# initialize player x, y position
px, py = SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.8

SPRITE_SIZE = 32
SCALED_SPRITE_SIZE = SPRITE_SIZE * 4

# ship image
spriteSheetFile = 'assets/spriteSheet.png'
spriteSheet = pg.image.load(spriteSheetFile)


SHIPS = {
    'PLAYER': spriteSheet.subsurface(0, 1100, 256, 200),
    'SHIELDED': spriteSheet.subsurface(0, 1300, 256, 200),
    'FGRADE': spriteSheet.subsurface(0, 900, 256, 200),
    'DGRADE': spriteSheet.subsurface(0, 700, 256, 200),
    'CGRADE': spriteSheet.subsurface(0, 500, 256, 200),
    'MINIBOSS': spriteSheet.subsurface(0, 300, 256, 200),
    'BOSS': spriteSheet.subsurface(0, 0, 256, 300)
}

# bullet image
PBULLETS = {
    'SmallOne': spriteSheet.subsurface(256, 1400, 84, 100),
    'SmallTwo': spriteSheet.subsurface(256, 1300, 84, 100),
    'BigOne': spriteSheet.subsurface(340, 1400, 80, 100),
    'BigTwo': spriteSheet.subsurface(340, 1300, 80, 100)
}

FBULLETS = {
    'SmallOne': spriteSheet.subsurface(256, 1100, 84, 100),
    'SmallTwo': spriteSheet.subsurface(256, 1200, 84, 100),
    'BigOne': spriteSheet.subsurface(340, 1100, 80, 100),
    'BigTwo': spriteSheet.subsurface(340, 1200, 80, 100)
}

itemSheetFile = 'assets/i_are_spaceship.png'
itemSheet = pg.image.load(itemSheetFile)
    
ITEMS = {
    'Powerup': itemSheet.subsurface(0, 0, 16, 16),
    'Lifeup': itemSheet.subsurface(16, 48, 16, 16),
    '1timeshield': itemSheet.subsurface(0, 48, 16, 16),
    'Bomb': itemSheet.subsurface(0, 48, 16, 16),
    'Savedshield': itemSheet.subsurface(48, 0, 16, 16)
}