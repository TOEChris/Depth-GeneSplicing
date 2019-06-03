import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
os.environ['KIVY_IMAGE'] = 'pil'
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import OptionProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.garden.collider import Collide2DPoly

from kivy.core.window import Window
from kivy.graphics import Rectangle, RoundedRectangle, Color, Line, Quad, Mesh, Ellipse
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.image import Image as uixImage
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, WipeTransition, RiseInTransition
from kivy.uix.progressbar import ProgressBar
from kivy.uix.modalview import ModalView

import time
import random
import serial
import io
import pygame

from functools import partial
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import socketserver

kv = '''
#: import FadeTransition kivy.uix.screenmanager.FadeTransition
ScreenManagement:
    id: manager
    CompScreen:
    GeneScreen:
 
<CompScreen>:
    stat1: rfidStatus1
    stat2: rfidStatus2
    stat3: rfidStatus3

    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "assets/GeneSplicerBackGround.jpg"
        Rectangle:
            source: 'assets/kegPic.png'
            size: 235, 235
            pos: 1050, 340
    Label:
        font_size: 56
        font_name: 'LiquidCrystal-Normal.otf'
        color: (0,1,0,1)
        text: "ENGAGED"
        pos: -680,-325
    Label:
        id: rfidStatus1
        font_size: 56
        font_name: 'LiquidCrystal-Normal.otf'
        color: (.909,.133,.133,1)
        text: "MISSING"
        pos: -245,-325
    Label:
        id: rfidStatus2
        font_size: 56
        font_name: 'LiquidCrystal-Normal.otf'
        color: (.909,.133,.133,1)
        text: "MISSING"
        pos: 195,-325
    Label:
        id: rfidStatus3
        font_size: 56
        font_name: 'LiquidCrystal-Normal.otf'
        color: (.909,.133,.133,1)
        text: "MISSING"
        pos: 618,-325

<GeneScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "assets/TerminalBackground.jpg"
    Base:
        id: base
        rows: 2
        Top:
            rows: 2
            id: topBox
            Cata:
                id: catalyst
                canvas.before:
                    Color:
                        rgb: .62, .218, .008
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgb: .206, .073, .008
                    RoundedRectangle:
                        size: self.width - 50, self.height - 50
                        pos: self.x + 25, self.y + 25
                canvas:
                    Color:
                        rgb: .525, .218, .008
                    Mesh:
                        mode: 'triangle_strip'
                        vertices: self.meshPointsTop
                        indices: self.meshIndTop
                    Mesh:
                        mode: 'triangle_fan'
                        vertices: self.meshPointsBot
                        indices: self.meshIndBot
                    Color:
                        rgb: 0.3,0.3,0.3
                    Rectangle:
                        group: 'stage'
                        size: 5, self.height - 50
                        pos: self.width/6, self.y + 25
                    Rectangle:
                        group: 'stage'
                        size: 5, self.height - 50
                        pos: self.width/6 *2, self.y + 25
                    Rectangle:
                        group: 'stage'
                        size: 5, self.height - 50
                        pos: self.width/6 *3, self.y + 25
                    Rectangle:
                        group: 'stage'
                        size: 5, self.height - 50
                        pos: self.width/6 *4, self.y + 25
                    Rectangle:
                        group: 'stage'
                        size: 5, self.height - 50
                        pos: self.width/6 *5, self.y + 25
                    Color:
                        group: 'coverColor'
                        rgba: 0,0,0,1
                    Rectangle:
                        group:'cover'
                        size: self.width/6-5, self.height-50
                        pos: self.width/6+5, self.y+25
                    Color:
                        group: 'coverColor'
                        rgba: 0,0,0,1
                    Rectangle:
                        group:'cover'
                        size: self.width/6-5, self.height-50
                        pos: self.width/6*2+5, self.y+25
                    Color:
                        group: 'coverColor'
                        rgba: 0,0,0,1
                    Rectangle:
                        group: 'cover'
                        size: self.width/6-5, self.height-50
                        pos: self.width/6*3+5, self.y+25
                    Color:
                        group: 'coverColor'
                        rgba: 0,0,0,1
                    Rectangle:
                        group:'cover'
                        size: self.width/6-5, self.height-50
                        pos: self.width/6*4+5, self.y+25
                    Color:
                        group: 'coverColor'
                        rgba: 0,0,0,1
                    Rectangle:
                        group:'cover'
                        size: self.width/6-40, self.height-50
                        pos: self.width/6*5+5, self.y+25
                    RoundedRectangle:
                        group: 'cover'
                        size: 40, self.height-50
                        pos: self.width - 65, self.y+25
                    Color:
                        group: 'lineColor'
                        rgba: 1,.404,0,1
                    Line:
                        id: line
                        points: self.points
                        width: self.linewidth
                        close: self.close
                    Color:
                        group: 'cataTriColor'
                        rgba: .475, .486, .478, 1
                    Rectangle:
                        group: 'cataTri'
                        source: 'assets/cataTri.png'
                        size: 32, 32
                        pos: self.points[-2]-5, self.points[-1]-18
            Div:
                id: status
                size_hint: 1, 0.2
                
                Image:
                    id: gifLeft
                    source: 'assets/particleLeft.gif'
                    anim_delay: 0
                    allow_stretch: True
                    keep_ratio: False
                    color: 1,1,1,0.85
                    size: 960, 90
                    pos: 0, status.y
                Image:
                    id: gifRight
                    source: 'assets/particleRight.gif'
                    anim_delay: 0
                    allow_stretch: True
                    keep_ratio: False
                    color: 1,1,1,0.85
                    size: 960, 90
                    pos: 960, status.y
                GenLabel:
                    id: statusText
                    text: 'Initial Startup'
                    pos: status.x + status.width/6, status.y-4
                    color: .475, .486, .478, 1

                GenLabel:
                    id: timer
                    text: 'TIME LEFT'
                    pos: status.x + status.width/4 * 3, status.y-4
                    color: .475, .486, .478, 1
            
                GenLabel:
                    id: timerData
                    text: '-'
                    pos: status.x + status.width/4 *3 + 200, status.y-4
            
                GenLabel:
                    id: title
                    text: 'GENE SPLICER'
                    pos: status.x + status.width/2.1, status.y-4
                    color: .475, .486, .478, 1
                        
        Bottom:
            cols: 3
            id: bottomBox
            Div:
                id: pressure
                size: root.size
                pos: root.pos
                canvas:
                    Color:
                        group: 'background'
                        rgb: .250, .60, .175
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgb: .086, .231, .051
                    RoundedRectangle:
                        size: self.width - 50, self.height - 50
                        pos: self.x + 25, self.y + 25
                    Color:
                        rgb: .250, .60, .175
                    RoundedRectangle:
                        size: (self.width*4)/6, self.height/6
                        pos: self.width/6, self.height/1.2
                GenLabel:
                    font_size: 56
                    pos: pressure.width/2.4, pressure.height/1.225
                    text: 'Pressure'
                GenLabel:
                    id: pressInfo
                    font_size: 116
                    pos: pressure.width/2 - 45, pressure.height/4
                    text: 'Waiting...'
                    color: 1,1,1,1
                GenLabel:
                    id: targetLabel
                    pos: pressure.width/4, pressure.height/2
                    text: 'Target:'
                GenLabel:
                    id: targetData
                    pos: pressure.width/1.75, pressure.height/2
                    text: '9.15 Atm'
                
            Div:
                id: voltage
                size: root.size
                pos: root.pos
                canvas:
                    Color:
                        group: 'background'
                        rgb: .008, .435, .620
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgb: .008, .145, .206
                    RoundedRectangle:
                        size: self.width - 50, self.height - 50
                        pos: self.x + 25, self.y + 25
                    Color:
                        rgb: .008, .435, .620
                    RoundedRectangle:
                        size: (((root.width*4)/6)/3), self.height/6
                        pos: ((root.width/3)+(root.width/18)), self.height/1.2
                GenLabel:
                    font_size: 56
                    pos: 920, voltage.height/1.225
                    text: 'Voltage'
                GenLabel:
                    id: voltInfo
                    font_size: 116
                    pos: 920, voltage.height/4
                    text: 'Waiting...'
                    color: 1,1,1,1
                GenLabel:
                    id: targetLabel
                    pos: 830, voltage.height/2
                    text: 'Target:'
                GenLabel:
                    id: targetData
                    pos: 992, voltage.height/2
                    text: '32V'
            Div:
                id: temperature
                size: root.size
                pos: root.pos
                canvas:
                    Color:
                        group: 'background'
                        rgb: .62, .60, .012
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgb: .278, .275, .004 
                    RoundedRectangle:
                        size: self.width - 50, self.height - 50
                        pos: self.x + 25, self.y + 25
                    Color:
                        rgb: .62, .60, .012
                    RoundedRectangle:
                        size: (((root.width*4)/6)/3), self.height/6
                        pos: ((root.width/3)*2+(root.width/18)), self.height/1.2
                GenLabel:
                    font_size: 56
                    pos: 1550, temperature.height/1.225
                    text: 'Temperature'
                GenLabel:
                    id: tempInfo
                    font_size: 116
                    pos: 1550, temperature.height/4
                    text: 'Waiting...'
                    color: 1,1,1,1
                GenLabel:
                    id: targetLabel
                    pos: 1500, temperature.height/2
                    text: 'Target:'
                GenLabel:
                    id: targetData
                    pos: 1650, temperature.height/2
                    text: '100 C'
'''

portCom = 'COM3'    #component Arduino (Component_Com)
portBut = 'COM4'    #cata button Arduino
serCom = serial.Serial(portCom, baudrate=9600, timeout = 0)
serBut = serial.Serial(portBut, baudrate = 19200, timeout = 0)
serCom.flush()
serBut.flush()
sioCom = io.TextIOWrapper(io.BufferedRWPair(serCom,serCom), newline='\r\n', encoding = 'utf-8')  #initialization
sioBut = io.TextIOWrapper(io.BufferedRWPair(serBut,serBut), newline='\r\n', encoding = 'utf-8')


pygame.mixer.pre_init(44100, -16, 2, 2048)              #sounds initialization
#needed to give enough time for the port to initiate!!
time.sleep(3)

#Server and handler classes

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    #only HTTP request needed, sent by Client
    def do_GET(self):
        app = App.get_running_app()
        self._set_headers()
        if (self.path == "/status"):
            if (app.instance.ids.catalyst.puzzleSolved):
                self.wfile.write(bytes("Splicer Won", 'utf-8'))
            elif (app.manager.current == "CompScreen"):
                rfidCurrent = app.rfidCurrent
                compStatus = {'H.DNA': '', 'C.DNA': '', 'Cata': ''}
                i = 0
                returnString = '|'
                for key in list(compStatus):
                    compStatus[key] = rfidCurrent[i]
                    returnString += ' {0}: {1} |'.format(key, compStatus[key])
                    i+=1
                self.wfile.write(bytes(returnString, 'utf-8'))
            elif (app.manager.current == 'GeneScreen'):
                self.wfile.write(bytes(app.instance.ids.statusText.text, "utf-8"))

        elif(self.path == "/win"):
            self.wfile.write(bytes("Splicer Triggered", "utf-8"))
            app.instance.ids.catalyst.puzzleSolved = True
            if (app.manager.current == "CompScreen"):
                Clock.schedule_once(partial(app.switchScreen, "GeneScreen"), 0.5)
                app.win("Comp")
            else:
                app.win("Gene")
        elif(self.path == "/reset"):
            self.wfile.write(bytes("Splicer Reset", "utf-8"))
            app.reset("Full")

#seperate thread is made to manage all network requests, class shouldn't need to be changed
class Server(socketserver.ThreadingMixIn, HTTPServer):
    def process_requests(self, *args):
        while(True):
            self.handle_request()

class ScreenManagement(ScreenManager):
    pass
class GeneScreen(Screen):
    pass
class CompScreen(Screen):
    def build(self, *args):
        self.labels = [self.stat1, self.stat2, self.stat3] #taken from the kv string, needed to reference in Python code

#called by and only by the cata button thread for when the cata button is pressed
def buttonTrig():
    app = App.get_running_app()
    while True:
        status = sioBut.readline()
        if ('1' in status):
            app.instance.ids.catalyst.jump()
            app._sound_library['cata'].play()

class Cata(FloatLayout):
    puzzleSolved = False
    gravity = 0.06  #for flappy bird current point
    velocity = 0    #dictates up or down direction
    accel = 0       #dictates change in velocity, considers gravity and current velocity
    close = BooleanProperty(False) #constant property, dont change
    points = ListProperty([28,850]) #points in the line throughout the wrong puzzle. Change these two points if you want to change the first point

    #The points for the bottom boundary polygon in catalyst 
    meshPointsBot = [150,655,0,0, 321,875,0,0, 640,850,0,0, 960,950,0,0, 1280,950,0,0, 1600,800,0,0, 1895,700,0,0, 1895,655,0,0]
    #Collider polygon is seperate from the visible polygon. If you change the boundaries, make sure the collider mesh corresponds
    meshBotCollide = Collide2DPoly([float(x) for x in meshPointsBot if x != 0], cache=True)
    #determines what order the poitns in meshPointsBot are drawn
    meshIndBot = [0,1,2,3,4,5,6,7]

    #Same as above however this was harder to fill. The visible and collider polygon share similar but not exactly the same points
    meshPointsTop = [63,1055,0,0, 321,955,0,0, 640,955,0,0, 960,1000,0,0, 1280,1030,0,0, 1600,975,0,0, 1895,750,0,0, 1895,1055,0,0, 960,1055,0,0, 640,1055,0,0]
    #IF YOU NEED TO CHANGE COLLIDER POLYGON
    #1. Adjust the visual (meshPointsTop or meshPointsBot) to what you want
    #2. Outline the points of the collider by starting up and clicking on the vertexes or points you want to outline the collider
    #3. The points will output to the console
    #4. Put the points into the meshTopCollide or meshBotCollide accordingly. There may be some slight offset in the points entered and where it outputs on screen
    #because of the window/display translation so adjust accordingly
    meshTopCollide = Collide2DPoly([63,1055, 321,955, 640,955, 960,1000, 1280,1030, 1391,989, 1895,750, 1895,1055, 63,1055])
    #Order is different to fill the polygon. It is purely for visuals
    meshIndTop = [0,1,2,3,4,5,6,7,5,8,9,1,7,0]
    counter = 0 #used to track when to stamp the current point to create the line
    crossed = [False, False, False, False, False] #flags to see what stages have been cleared
    linewidth = NumericProperty(3)
    #used to calculate the timer data. Change if the first stage marker position is changed
    nextPoint = 321
    prevPoint = 28
    #used to pulse the line color
    colorDir = False

    def __init__(self, **kwargs):
        super(Cata, self).__init__(**kwargs)
        self.app = App.get_running_app()
        #DEBUG code if you need to see the outline of either collider polygon
        #with self.canvas:
        #    Color(rgb=(1,0,0))
        #    Line(points=(63,1055, 321,955, 640,955, 960,1000, 1280,1030, 1391,989, 1895,750, 1895,1055, 63,1055))

    #is called by a Clock schedule to move cata point and check fail and success conditions
    def update_points(self, *args):
        app = self.app
        temp = []   #used to store the most recent two points of the cata line
        temp.append(self.points.pop())
        temp.append(self.points.pop())
        if (app.started): #only has to check success and fail conditions if the trail has started
            if ((float(temp[1]), float(temp[0])) in self.meshBotCollide or (float(temp[1]), float(temp[0])) in self.meshTopCollide): #checks if point is out of bounds
                app.messagePopUp("CATALYST IMBALANCE", 56, 510)
                app.reset("Stage")
                app._sound_library['fail'].play()
                app.switchSound('backEnd', 0, 0)
                return
            #timer data, proportion of distance crossed
            if (not self.puzzleSolved):
                timerData = ((self.nextPoint - round(temp[1],1))) / ((self.nextPoint - self.prevPoint) / 10)
                app.instance.ids.timerData.text = ('%.2f' % round(timerData,2))
                if (timerData < 3):
                    app.instance.ids.timerData.color = (1,.149,.161,1)
                    if (not app.stageCheck(temp[1])):
                        return
                else:
                    app.instance.ids.timerData.color = (1,1,1,1)
        
        #pulses cata line color
        lineColor = app.instance.ids.catalyst.canvas.get_group('lineColor')[0].rgba[2]
        if (lineColor >= .235):
            self.colorDir = False
        elif (lineColor < .404):
            self.colorDir = True
        if (self.colorDir):
            lineColor += .02
        else:
            lineColor -= .02
        app.instance.ids.catalyst.canvas.get_group('lineColor')[0].rgba[1] = lineColor

        #acceleration per height region
        self.accel += self.gravity
        toCheck = self.accel
        if (toCheck < 4 and toCheck > 0): 
            self.accel *= 1.06
        elif (toCheck < 0):
            self.accel *= 0.8
        elif (toCheck == 0):
            self.accel = 0.25

        self.velocity += self.accel
        
        if (app.started):
            temp[1] += 1.1
        self.points.append(temp[1])

        #changes the color of the stage current values if the target has been met
        for pos,x in enumerate(self.crossed):
            if (not app.started):
                if (app.tempCurrent == app.tempTargets[0] and app.instance.ids.tempInfo.color == [1,1,1,1]):
                    app.instance.ids.tempInfo.color = (0,1,0,1)
                elif (not app.tempCurrent == app.tempTargets[0] and app.instance.ids.tempInfo.color == [0,1,0,1]):
                    app.instance.ids.tempInfo.color = (1,1,1,1)
                if (app.voltCurrent == app.voltTargets[0] and app.instance.ids.voltInfo.color == [1,1,1,1]):
                    app.instance.ids.voltInfo.color = (0,1,0,1)
                elif (not app.voltCurrent == app.voltTargets[0] and app.instance.ids.voltInfo.color == [0,1,0,1]):
                    app.instance.ids.voltInfo.color = (1,1,1,1)
                if (app.presCurrent == app.presTargets[0] and app.instance.ids.pressInfo.color == [1,1,1,1]):
                    app.instance.ids.pressInfo.color = (0,1,0,1)
                elif (not app.presCurrent == app.presTargets[0] and app.instance.ids.pressInfo.color == [0,1,0,1]):
                    app.instance.ids.pressInfo.color = (1,1,1,1)
                break
            elif (not x):
                if (app.tempCurrent == app.tempTargets[pos+1] and app.instance.ids.tempInfo.color == [1,1,1,1]):
                    app.instance.ids.tempInfo.color = (0,1,0,1)
                elif (not app.tempCurrent == app.tempTargets[pos+1] and app.instance.ids.tempInfo.color == [0,1,0,1]):
                    app.instance.ids.tempInfo.color = (1,1,1,1)
                if (app.voltCurrent == app.voltTargets[pos+1] and app.instance.ids.voltInfo.color == [1,1,1,1]):
                    app.instance.ids.voltInfo.color = (0,1,0,1)
                elif (not app.voltCurrent == app.voltTargets[pos+1] and app.instance.ids.voltInfo.color == [0,1,0,1]):
                    app.instance.ids.voltInfo.color = (1,1,1,1)
                if (app.presCurrent == app.presTargets[pos+1] and app.instance.ids.pressInfo.color == [1,1,1,1]):
                    app.instance.ids.pressInfo.color = (0,1,0,1)
                elif (not app.presCurrent == app.presTargets[pos+1] and app.instance.ids.pressInfo.color == [0,1,0,1]):
                    app.instance.ids.pressInfo.color = (1,1,1,1)
                break

        temp[0] -= self.velocity
        if (app.started):
            if (temp[0] > 1150):
                temp[0] = 1150
            elif (temp[0] < 665):
                temp[0] = 665
        else:
            if (temp[0] > 1000):
                temp[0] = 1000
            elif(temp[0] < 700):
                temp[0] = 700
        temp[0] = round(temp[0], 1)
        #calculated points are reinserted into the full list of Line points
        self.points.append(temp[0])
        
        if (self.velocity > 0):
            self.velocity = 0
        
        #if x (currently 10) cycles have ran, appends the points twice so the line is continued
        if (app.started):
            if (self.counter == 10):
                self.points.append(temp[1])
                self.points.append(temp[0])
                self.counter = 0
            else:
                self.counter += 1
    #recalculates acceleration everytime the cata point jumps
    def jump(self, *args):
        currentAccel = self.accel
        try:
            toCheck = self.points[-1]
        except IndexError:
            return
        if (toCheck > 975 and not currentAccel == -0.20):
            self.accel = -0.20
        elif(toCheck > 860 and not currentAccel == -0.27) :
            self.accel = -0.27
        elif(toCheck > 800 and not currentAccel == -0.32):
            self.accel = -0.32
        elif(not currentAccel == -0.4):
            self.accel = -0.4
class Top(GridLayout):
    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)
class Bottom(GridLayout):
    def __init__(self, **kwargs):
        super(Bottom, self).__init__(**kwargs)
class Div(Widget):
    def __init__(self, **kwargs):
        super(Div, self).__init__(**kwargs)      
class Base(GridLayout):
    def __init__(self, **kwargs):
        super(Base, self).__init__(**kwargs)
    #function to print the clicked coordinates to the console
    def on_touch_down(self, touch):
        print(touch.pos)
#Generic Label
class GenLabel(Label):
    def __init__(self, **kwargs):
        self.font_name = 'ColdWarm.otf'
        self.font_size = 48
        super(GenLabel, self).__init__(**kwargs)

class CircularProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)

        # Set constant for the bar thickness
        self.thickness = 64
        # Create a direct text representation
        self.label = CoreLabel(text="0%", font_size=self.thickness)

        # Initialise the texture_size variable
        self.texture_size = None

        # Refresh the text
        self.refresh_text()

        # Redraw on innit
        self.draw()
 
    def draw(self):
        self.pos = (800,330)
        with self.canvas:
            # Empty canvas instructions
            self.canvas.clear()

            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)
            Ellipse(pos=self.pos, size=self.size)
            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(0, 1, 0)
            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(0.001 if self.value_normalized == 0 else self.value_normalized*360))

            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))

            # Center and draw the progress text
            Color(1, 1, 1, 1)
            Rectangle(texture=self.label.texture, size=self.texture_size,
                      pos=(self.pos[0]+self.width/2 - self.texture_size[0]/2, self.pos[1] +self.height/2- self.texture_size[1]/2))
    def refresh_text(self):
        # Render the label
        self.label.refresh()

        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value):
        # Update the progress bar value
        self.value = value

        # Update textual value and refresh the texture
        self.label.text = str(int(self.value_normalized*100)) + "%"
        self.refresh_text()

        # Draw all the elements
        self.draw()




class SpliceApp(App):
    started = False
    wonLabel = InstructionGroup()
    errorLabel = InstructionGroup()
    transitionLabel = InstructionGroup()
    #The window that pops up when the puzzle is won
    view = ModalView(size_hint=(None, None), size=(700, 500))
    #Holds the label and progress bar in the pop up window
    grid = GridLayout(rows = 2)
   #variable to hold the update_points Clock event to check if its scheduled
    update = None   

    tempTargets = [100, 152, 405, 385, 275, 36, 0]
    #tempTargets = [0,0,0,0,0,0,0] #DEBUG
    voltTargets = [32, 7, 24, 228, 255, 4, 0]
    #voltTargets = [0,0,0,0,0,0,0] #DEBUG
    presTargets = [9.15, 8.65, 7.20, 7.00, 2.10, 2.35, 0.00]
    #presTargets = [0,0,0,0,0,0,0] #DEBUG
    tempCurrent = 0
    voltCurrent = 0
    presCurrent = 0
    rfidCurrent = ['No','No','No']
    currentMessage = False
    flashing = False
    screenSwitched = False

    def __init__(self, **kwargs):
        self.serRead = Clock.schedule_interval(self.serialRead, 0.025)
        super(SpliceApp, self).__init__(**kwargs)
    
    def switchScreen(self, *args):
        self.manager.current = args[0]

    #args[0] is the filename, args[1] is loops and arg[2] is channel number
    def switchSound(self, *args):
        if(pygame.mixer.Channel(args[2]).get_busy()):
            pygame.mixer.Channel(args[2]).stop()
        pygame.mixer.Channel(args[2]).play(self._sound_library[args[0]], args[1])

    def serialRead(self, *args):
        #returns Serial data from Arduino in list structure
        data = self.getLatestStatus()
        if (not data):
            return
        del data[0]    #gets rid of Start marker (S)
        del data[-1]   #gets rid of End marker (E)

        #loop takes the first two items off the line until its empty (Ex: [R, 10.175])
        while(len(data) >= 2):
            if(self.manager.current == "GeneScreen"):
                if(data[0] == 'W' and not self.started):
                    if (str(data[1]) == 'True'):
                        if (self.compCheck(0) == False):
                            if (not self.currentMessage):
                                self.messagePopUp("INITIAL TARGETS NOT MET", 56, 490)
                                self._sound_library['fail'].play()
                                self.switchSound('backEnd', 0, 0)
                            serCom.write(b'S\r\n') #sends back flag to Arduino to switch back to pre-trial mode
                            break
                        else:
                            if (not self.currentMessage):
                                self.started = True
                                self.instance.ids.catalyst.points.append(self.instance.ids.catalyst.points[-2])
                                self.instance.ids.catalyst.points.append(self.instance.ids.catalyst.points[-2])
                                self.instance.ids.catalyst.canvas.get_group('cataTriColor')[0].rgba[3] = 0 #gets rid of silver triangle
                                self.instance.ids.statusText.text = 'STAGE 1 OF 6'
                                self.instance.ids.temperature.children[0].text = str(self.tempTargets[1]) + " C"
                                self.instance.ids.pressure.children[0].text = str(self.presTargets[1]) + " ATM"
                                self.instance.ids.voltage.children[0].text = str(self.voltTargets[1]) + "V"
                                self._sound_library['backStart'].play()
                                Clock.schedule_once(partial(self.switchSound, "backLoop", -1, 0), self._sound_library['backStart'].get_length())
                            else:
                                serCom.write(b'S\r\n')
                elif (data[0] == 'T'):
                    self.tempCurrent = round(float(data[1]), 2)
                    textToSet = str(self.tempCurrent)
                    self.instance.ids.tempInfo.text = textToSet
                elif(data[0] == 'R'):
                    if (float(data[1]) < 0):
                        textToSet = "0.000"
                    else:
                        self.presCurrent = float(data[1])
                        textToSet = str(self.presCurrent).ljust(5, '0')
                    self.instance.ids.pressInfo.text = textToSet
                elif(data[0] == 'V'):
                    self.voltCurrent = int(data[1])
                    textToSet = str(self.voltCurrent)
                    self.instance.ids.voltInfo.text = textToSet
            else:
                if(data[0] == 'C'):
                    allCorrect = True
                    for pos, x in enumerate(data[1]):
                        if (x == 'Y'):
                            self.compScreen.labels[pos].color =(0,1,0,1)
                            self.compScreen.labels[pos].text = "ENGAGED"
                            self.rfidCurrent[pos] = 'Yes'
                        elif (x == 'N'):
                            allCorrect = False
                            self.compScreen.labels[pos].color =(.909, .133, .133, 1)
                            self.compScreen.labels[pos].text = "MISSING"
                            self.rfidCurrent[pos] = 'No'
                        elif (x == 'I'):
                            allCorrect = False
                            self.compScreen.labels[pos].color = (.843, .384, .098, 1)
                            self.compScreen.labels[pos].text = "UNSEQUENCED"
                            self.rfidCurrent[pos] = 'UnSeq'
                    if (allCorrect and not self.screenSwitched):
                        self.screenSwitched = True
                        self.compScreen.canvas.add(self.transitionLabel)
                        if (not self.update):
                            self.update = Clock.schedule_interval(self.instance.ids.catalyst.update_points, .016)
                        serCom.write(b'J\r\n') #sends flag back to Ardunio that lets it know the puzzle recognized to switch screen
                        Clock.schedule_once(partial(self.switchScreen, "GeneScreen"), 2)
            del data[0:1]
    #args[0] is the current x pos of the latest cata line point
    def stageCheck(self, *args):
        temp = args[0]
        cata = self.instance.ids.catalyst

        if (not cata.crossed[0] and temp >= 321):
            if (self.compCheck(1) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.prevPoint = 321
            cata.nextPoint = 647
            cata.crossed[0] = True
            cata.canvas.get_group("coverColor")[0].rgba = [0,0,0,0]
            self.instance.ids.statusText.text = 'STAGE 2 OF 6'
            self.instance.ids.temperature.children[0].text = str(self.tempTargets[2]) + " C"
            self.instance.ids.pressure.children[0].text = str(self.presTargets[2]) + " ATM"
            self.instance.ids.voltage.children[0].text = str(self.voltTargets[2]) + "V"
            self._sound_library['stage1'].play()
        elif(not cata.crossed[1] and temp >= 647):
            if (self.compCheck(2) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.prevPoint = 647
            cata.nextPoint = 970
            cata.crossed[1] = True
            cata.canvas.get_group("coverColor")[1].rgba = [0,0,0,0]
            self.instance.ids.statusText.text = 'STAGE 3 OF 6'
            self.instance.ids.temperature.children[0].text = str(self.tempTargets[3]) + " C"
            self.instance.ids.pressure.children[0].text = str(self.presTargets[3]) + " ATM"
            self.instance.ids.voltage.children[0].text = str(self.voltTargets[3]) + "V"
            self._sound_library['stage2'].play()
        elif(not cata.crossed[2] and temp >= 970):
            if (self.compCheck(3) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.prevPoint = 970
            cata.nextPoint = 1290
            cata.crossed[2] = True
            cata.canvas.get_group("coverColor")[2].rgba = [0,0,0,0]
            self.instance.ids.statusText.text = 'STAGE 4 OF 6'
            self.instance.ids.temperature.children[0].text = str(self.tempTargets[4]) + " C"
            self.instance.ids.pressure.children[0].text = str(self.presTargets[4]) + " ATM"
            self.instance.ids.voltage.children[0].text = str(self.voltTargets[4]) + "V"
            self._sound_library['stage3'].play()
        elif(not cata.crossed[3] and temp >= 1290):
            compResults = self.compCheck(4)
            if (self.compCheck(4) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.prevPoint = 1290
            cata.nextPoint = 1614
            cata.crossed[3] = True
            cata.canvas.get_group("coverColor")[3].rgba = [0,0,0,0]
            self.instance.ids.statusText.text = 'STAGE 5 OF 6'
            self.instance.ids.temperature.children[0].text = str(self.tempTargets[5]) + " C"
            self.instance.ids.pressure.children[0].text = str(self.presTargets[5]) + " ATM"
            self.instance.ids.voltage.children[0].text = str(self.voltTargets[5]) + "V"
            self._sound_library['stage4'].play()
        elif(not cata.crossed[4] and temp >= 1614):
            if (self.compCheck(5) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.prevPoint = 1614
            cata.nextPoint = 1910
            cata.crossed[4] = True
            cata.canvas.get_group("coverColor")[4].rgba = [0,0,0,0]
            self.instance.ids.statusText.text = 'STAGE 6 OF 6'
            self.instance.ids.temperature.children[0].text = str(self.tempTargets[6]) + " C"
            self.instance.ids.pressure.children[0].text = str(self.presTargets[6]) + " ATM"
            self.instance.ids.voltage.children[0].text = str(self.voltTargets[6]) + "V"
            self._sound_library['stage5'].play()
        elif(temp >= 1910):
            if (self.compCheck(6) == False):
                self.reset("Stage")
                self.messagePopUp("TARGETS NOT MET", 64, 520)
                self._sound_library['fail'].play()
                self.switchSound('backEnd', 0, 0)
                return False
            cata.puzzleSolved = True
            self.win("Gene")
            self.switchSound('backEnd', 0, 0)
        return True

    #checks if the 3 stations have met their targets args[0]: the current stage
    def compCheck(self, *args):
        def flipColors(*args):
            bottom = self.instance.ids
            if (args[1] == 6):
                self.flashing = False
                return
            comps = args[0]
            voltOrig = Color(rgba = (.008, .435, .620, 1))
            presOrig = Color(rgba = (.250, .60, .175, 1))
            tempOrig = Color(rgba = (.62, .60, .012, 1))
            if (comps[0]):
                if (bottom.temperature.canvas.get_group('background')[0].rgba == tempOrig.rgba):
                    bottom.temperature.canvas.get_group('background')[0].rgba = (.6275,0,0,1)
                else:
                    bottom.temperature.canvas.get_group('background')[0].rgba = tempOrig.rgba
            if (comps[1]):
                if (bottom.pressure.canvas.get_group('background')[0].rgba == presOrig.rgba):
                    bottom.pressure.canvas.get_group('background')[0].rgba = (.6275,0,0,1)
                else:
                    bottom.pressure.canvas.get_group('background')[0].rgba = presOrig.rgba
            if (comps[2]):
                if (bottom.voltage.canvas.get_group('background')[0].rgba == voltOrig.rgba):
                    bottom.voltage.canvas.get_group('background')[0].rgba = (.6275,0,0,1)
                else:
                    bottom.voltage.canvas.get_group('background')[0].rgba = voltOrig.rgba
            Clock.schedule_once(partial(flipColors, comps, args[1]+1), .5) 

        stage = args[0]
        wrongComps = [False, False, False]
        if (not self.tempCurrent == self.tempTargets[stage]):
            wrongComps[0] = True
        if (not self.presCurrent == self.presTargets[stage]):
            wrongComps[1] = True
        if (not self.voltCurrent == self.voltTargets[stage]):
            wrongComps[2] = True

        if (True in wrongComps):
            if (not self.flashing):
                self.flashing = True
                flipColors(wrongComps, 0) #args[0]: the stages to flash args[1]: a counter to keep track of how many times to call the flipColors function
            return False
        return True
       
    def build(self):
        won = self.wonLabel
        won.add(Color(0,0,0,1))
        won.add(Rectangle(size=(1000, 190), pos= (450, 520)))
        won.add(Color(0,1,0,1))
        won.add(Rectangle(size=(980, 170), pos= (460, 530)))
        won.add(Color(1,1,1,1))
        label = CoreLabel(font_size=64, font_name='basica.ttf', text = 'SPLICING COMPLETE')
        label.refresh()
        won.add(Rectangle(texture=label.texture, size= label.size, pos=(525, 580)))

        error = self.errorLabel
        error.add(Color(0,0,0,1))
        error.add(Rectangle(size=(1000, 210), pos= (450, 520)))
        error.add(Color(1,.149,.161,1))
        error.add(Rectangle(size=(980, 190), pos= (460, 530)))
        error.add(Color(1,1,1,1))

        trans = self.transitionLabel
        trans.add(Color(0,0,0,1))
        trans.add(Rectangle(size=(1000, 210), pos= (450, 520)))
        trans.add(Color(.250, .80, .175))
        trans.add(Rectangle(size=(980, 190), pos= (460, 530)))
        trans.add(Color(1,1,1,1))
        label = CoreLabel(font_size=84, font_name='basica.ttf', text = 'INITIALIZING')
        label.refresh()
        trans.add(Rectangle(texture=label.texture, size= label.size, pos=(625, 580)))

        self.manager = ScreenManagement(transition = FadeTransition(duration=0.8))
        self.instance = GeneScreen(name='GeneScreen')
        self.compScreen = CompScreen(name='CompScreen')
        self.compScreen.build()
        self.manager.add_widget(self.instance)
        self.manager.add_widget(self.compScreen)
        self.manager.current = 'CompScreen'
                                                                                                                                                       
        pygame.mixer.init()
        pygame.init()

        self._sound_library = {
            "backStart": pygame.mixer.Sound('audio/start.wav',),
            "backLoop": pygame.mixer.Sound('audio/loop.wav'),
            "backEnd": pygame.mixer.Sound('audio/end.wav'),
            "fail": pygame.mixer.Sound('audio/fail.wav'),
            "complete": pygame.mixer.Sound('audio/complete.wav'),
            "success": pygame.mixer.Sound('audio/success.wav'),
            "cata": pygame.mixer.Sound('audio/cataNoise.wav'),
            "stage1": pygame.mixer.Sound('audio/stage1.wav'),
            "stage2": pygame.mixer.Sound('audio/stage2.wav'),
            "stage3": pygame.mixer.Sound('audio/stage3.wav'),
            "stage4": pygame.mixer.Sound('audio/stage4.wav'),
            "stage5": pygame.mixer.Sound('audio/stage5.wav')
        }
        self._sound_library['backStart'].set_volume(0.3)
        self._sound_library['backLoop'].set_volume(0.3)
        self._sound_library['backEnd'].set_volume(0.3)
        self._sound_library['cata'].set_volume(0.3)
        self.buttonThread = threading.Thread(target = buttonTrig).start() 
        return self.manager
        

    def getLatestStatus(self, *args):
        valid = False
        status = sioCom.readline()
        while serCom.inWaiting() > 0:
            status = sioCom.readline()
        if('W' in status):
            serCom.write(b'K\r\n')
            status = "S-W-True-E"
            return status.split('-')
        status = status.split('-')
        if (len(status) == 0):
            valid = True
        elif (('W' in status) or ('E' in status[-1] and 'S' in status[0])):
            valid = True
        else:
            return False
        return status
    
    def reset(self, *args):
        #reset points, clear line, reset data
        self.started = False
        cata = self.instance.ids.catalyst
        cata.points.clear()
        cata.points = [28,850]
        
        self.instance.ids.timerData.color = (1,1,1,1)
        self.instance.ids.timerData.text = "-"
        self.instance.ids.statusText.text = 'Initial Startup'

        cata.gravity = 0.05
        cata.velocity = 0
        cata.accel = 0
        cata.nextPoint = 321
        cata.prevPoint = 28
        #reset cata covers
        cata.crossed = [False, False, False, False, False]
        for x in cata.canvas.get_group('coverColor'):
            x.rgba = 0,0,0,1
        
        #reset individual component labels
        
        temp = self.instance.ids.temperature
        pres = self.instance.ids.pressure
        volt = self.instance.ids.voltage
        temp.children[0].text = str(self.tempTargets[0]) + " C"
        pres.children[0].text = str(self.presTargets[0]) + " ATM"
        volt.children[0].text = str(self.voltTargets[0]) + "V"

        #serial commune reset
        if (args[0] == "Full"):
            serCom.write(b'R\r\n')
            self.view.dismiss(force = True, animation = False)
            self.view.remove_widget(self.grid)
            self.grid = GridLayout(rows = 2)
            self.screenSwitched = False
            self.compScreen.canvas.remove(self.transitionLabel)
            self.instance.canvas.remove(self.wonLabel)
            self.instance.ids.catalyst.puzzleSolved = False
            Clock.schedule_once(partial(self.switchScreen, "CompScreen"), 0.5)
        #for when the fail the trial, not ERM reset
        elif (args[0] == "Stage"):
            serCom.write(b'S\r\n')
            self.instance.ids.catalyst.canvas.get_group('cataTriColor')[0].rgba[3] = 1
        
    def win(self, *args):
        def animate(appInst, *largs):
            progBar = appInst.view.children[0].children[0]
            if (appInst.view.children[0].children[0].value >= 100):
                self.winAnim.cancel()
                appInst.view.children[0].children[1].font_size = 48
                appInst.view.children[0].children[1].text = "Memory Write Successful"
                appInst._sound_library["success"].play()
                serCom.write(b'W\r\n')
            else:
                progBar.set_value(progBar.value + 1)
        if (args[0] == "Gene"):
            try:
                self.update.cancel()
            except AttributeError:
                pass
        if (len(self.grid.children) < 2):
            self.instance.ids.timerData.text = ('%.2f' % 0.0)
            self.grid.add_widget(GenLabel(text='Writing to Memory Module...', pos=(800, 900), font_size = 46, size_hint_y = 0.2))
            self.grid.add_widget(CircularProgressBar(id='progressBar', height=300, width=300, size_hint = (None,None)))
            with self.grid.canvas.before:
                uixImage(source='assets/blackBg.png', anim_delay=0, size= (670,470), pos=(623,307), allow_stretch = True, keep_ratio = False)
        
            self.view.add_widget(self.grid)
            self.view.open(animation=True)
            self.winAnim = Clock.schedule_interval(partial(animate, self), 0.03)
        

    def messagePopUp(self, *args):
        self.currentMessage = True
        def removeLabel(appInst, errorMess, *largs):
            error.remove_group("Text")
            appInst.instance.canvas.remove(errorMess)
            self.currentMessage = False
        error = self.errorLabel
        label = CoreLabel(font_size= args[1], font_name='basica.ttf', text = args[0])
        label.refresh()
        error.add(Rectangle(texture=label.texture, size= label.size, pos=(args[2], 600), group = "Text"))

        self.instance.canvas.add(error)
        Clock.schedule_once(partial(removeLabel, self, error), 3.5)

def serverRun(server_class=Server, handler_class=Handler, port=80):
    server_address = ('10.24.7.230', port)
    httpd = server_class(server_address, handler_class)
    print("serving at port",port)
    t = threading.Thread(target = httpd.process_requests)
    t.start()
    
if __name__ == '__main__':
    Builder.load_string(kv)
    serverRun()
    SpliceApp().run()