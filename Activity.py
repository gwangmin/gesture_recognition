
import pygame as pg
import pygame_gui as gui
import cv2

import global_vars

# Game UI interface class
class GameView(object):
    def __init__(self):
        self.done = False
        
    def start(self):
        pass

    def update(self):
        pass

    def getEvent(self, event):
        pass

    def draw(self, surf, manager):
        pass

'''
Game Title

'''
class Title(GameView):
    def __init__(self):
        super.__init__()
        self.titleRect = pg.rect.Rect(global_vars.SCREEN_WIDTH / 2, global_vars.SCREEN_HEIGHT / 4, -1, global_vars.SCREEN_HEIGHT / 5)
        self.btnRect = pg.rect.Rect(global_vars.SCREEN_WIDTH / 2, global_vars.SCREEN_HEIGHT / 2, global_vars.BUTTON_WIDTH, global_vars.BUTTON_HEIGHT)
        
        self.gameTitle = gui.elements.UILabel(relative_rect=self.titleRect,
                                              text='Gesture Bomber',
                                              anchor={'centerx':'centerx'})
        
        self.startBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                              text='Start',
                                              anchors={'centerx':'centerx'})
        self.rankBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                             text='Rank',
                                             anchors={'centerx': 'centerx', 'bottom_target':self.startBtn})
        self.settingBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                                text='Setting',
                                                anchors={'centerx': 'centerx', 'bottom_target':self.rankBtn})
        self.exitBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                             text='Exit',
                                             anchors={'centerx': 'centerx', 'bottom_target':self.settingBtn})
        
    def start(self):
        pass
    
    def update(self):
        pass
        
    def getEvent(self, event):
        # 만약 각 버튼이 눌리면
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.startBtn:
                self.stateName = 'Game'
                self.done = True
            elif event.ui_element == self.rankBtn:
                pass
            elif event.ui_element == self.settingBtn:
                self.stateName = 'Setting'
                self.done = True
            elif event.ui_element == self.exitBtn:
                pg.quit()
                # sys.quit()

    def draw(self, surf, manager):
        # onButton motion
        pass
        

    
class Rank(GameView):
    def __init__(self):
        super.__init__()
        
        self.btnRect = pg.rect.Rect(10, 10, global_vars.BUTTON_WIDTH, global_vars.BUTTON_HEIGHT)
        self.backBtn = gui.elements.UIButton(relative_rect=self.btnRect,
                                        text='Back',
                                        anchor={'left':'left', 'top':'top'})
        
    def start(self):
        pass

    def update(self):
        pass

    def getEvent(self, event):
        # exit to title
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.backBtn:
                self.stateName = 'Title'
                self.done = True

    def draw(self, surf, manager):
        pass

class Pause(GameView):
    def __init__(self):
        super.__init__()
        
        self.btnRect = pg.rect.Rect(10, 10, global_vars.BUTTON_WIDTH, global_vars.BUTTON_HEIGHT)
        self.backBtn = gui.elements.UIButton(relative_rect=self.btnRect,
                                        text='Back',
                                        anchor={'left':'left', 'top':'top'})
        
        self.labelRect = pg.rect.Rect(-1, global_vars.SCREEN_HEIGHT*0.2, -1, global_vars.SCREEN_HEIGHT / 5)
        
        self.stateLabel = gui.elements.UILabel(relative_rect=self.labelRect,
                                             anchor={'centerx':'centerx'})

    
    def start(self):
        pass

    def update(self):
        pass

    def getEvent(self, event):
        # exit to title
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.backBtn:
                self.stateName = 'Title'
                self.done = True

    def draw(self, surf, manager):
        pass
    

class Setting(GameView):
    def __init__(self):
        super.__init__()
        # make bgm sound: slider
        # make effect sound: slider
        # make LV: easy, normal, hard
        # make SYNC button
        
        self.btnRect = pg.rect.Rect(10, 10, global_vars.BUTTON_WIDTH, global_vars.BUTTON_HEIGHT)
        self.labelRect = pg.rect.Rect(global_vars.SCREEN_HEIGHT*0.2, 0, global_vars.BUTTON_WIDTH, global_vars.BUTTON_HEIGHT)
        self.sliderRect = pg.rect.Rect(0, 0, global_vars.BUTTON_WIDTH*3, global_vars.BUTTON_HEIGHT)
        
        self.backBtn = gui.elements.UIButton(relative_rect=self.btnRect,
                                        text='Back',
                                        anchor={'left':'left', 'top':'top'})
        
        self.bgmLabel = gui.elements.UILabel(relative_rect=self.labelRect, 
                                             text='BGM Sound')
        self.bgmSlider = gui.elements.UIHorizontalSlider(relative_rect=self.sliderRect, 
                                                         start_value=0, 
                                                         value_range=100,
                                                         anchor={'right_target':self.bgmLabel})
        
        self.effectLabel = gui.elements.UILabel(relative_rect=self.labelRect, 
                                                text='Effect Sound',
                                                anchor={'bottom_target':self.bgmLabel})
        self.effectSlider = gui.elements.UIHorizontalSlider(relative_rect=self.sliderRect, 
                                                            start_value=0, 
                                                            value_range=100,
                                                            anchor={'right_target':self.effectLabel})
        
        self.levelLabel = gui.elements.UILabel(relative_rect=self.labelRect, 
                                               text='Level',
                                               anchor={'bottom_target':self.effectLabel})
        self.easyBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                             text='Easy',
                                             anchor={'bottom_target':self.bgmLabel, 'right_target':self.levelLabel})
        self.normalBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                               text='Normal',
                                               anchor={'bottom_target':self.bgmLabel, 'right_target':self.easyBtn})
        self.hardBtn = gui.elements.UIButton(relative_rect=self.btnRect, 
                                             text='Hard',
                                             anchor={'bottom_target':self.bgmLabel, 'right_target':self.normalBtn})
        
        self.syncBtn = gui.elements.UIButton(relative_rect=self.labelRect, 
                                             text='Sync',
                                             anchor={'bottom_target':self.levelLabel})

    def start(self):
        pass

    def update(self):
        # update change of setting button (image)
        pass

    def getEvent(self, event):
        # exit to title
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.backBtn:
                self.stateName = 'Title'
                self.done = True
            if event.ui_element == self.easyBtn:
                pass
            if event.ui_element == self.normalBtn:
                pass
            if event.ui_element == self.hardBtn:
                pass
            if event.ui_element == self.syncBtn:
                self.stateName = 'Sync'
                self.done = True

    def draw(self, surf, manager):

        pass
    
'''
Sync 화면;
주의할 점: cv2로 화면을 띄우므로 충돌하지 않도록 주의
videocapture를 screen에 update
'''
class Sync(GameView):

    def __init__(self):
        super.__init__()

    def start(self):
        pass

    def update(self):
        # 단계 별 화면 변경
        '''
        1. 손바닥 landmark 확인
        2. gesture 번호 순서대로 인식을 반복
        3. sync 저장, 저장 완료 popup
        4. title로 돌아가시겠습니까? (특정 동작 시 진행)
        이전/다음 gesture로 화면을 구성해야할 듯
        '''
        pass

    def getEvent(self, event):
        # exit to title
        if event.type == '':
            self.stateName = 'Title'
            self.done = True

    def save(self, file):
        # save setting file, csv
        pass
    
    def draw(self, surf, manager):
        pass

class GameEnd(GameView):
    def __init__(self, isClear):
        super.__init__()
        self.isClear = isClear
        
        self.labelRect = pg.rect.Rect(-1, global_vars.SCREEN_HEIGHT*0.2, -1, global_vars.SCREEN_HEIGHT / 5)
        
        self.endLabel = gui.elements.UILabel(relative_rect=self.labelRect,
                                             anchor={'centerx':'centerx'})
        if self.isClear:
            self.endLabel.set_text('Game Clear')
        else:
            self.endLabel.set_text('Game Over')
        
    def start(self):
        pass

    def update(self):
        pass

    def getEvent(self, event):
        # 특정 제스처를 취하면 타이틀로 넘어감
        if event.type == global_vars.PINCH_EVENT:
            self.stateName = 'Title'
            self.done = True
            
    def draw(self, surf, manager):

            
        pass