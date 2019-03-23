import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import OptionProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.garden.collider import Collide2DPoly

from kivy.core.window import Window
from kivy.graphics import Rectangle, RoundedRectangle, Color, Line, Quad, Mesh
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.effectwidget import *

import time
import random
import serial
import io
from functools import partial
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import socketserver

kv = '''
<Base>
    rows: 2
    Top:
    Bottom:
<Top>
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
        canvas.after:
            Color:
                rgba: 0,0,1,1
            Line:
                id: line
                points: self.points
                width: self.linewidth
                close: self.close
    Div:
        id: status
        size_hint: 1, 0.2
        canvas:
            Color:
                rgb: 0,0,0
            Rectangle:
                size: self.size
                pos: self.pos
            Color:
                rgb: 1,1,1
        GenLabel:
            font_size: 56
            id: statusText
            text: 'Components Needed...'
            pos: status.x + status.width/6, status.y

        GenLabel:
            id: timer
            text: 'TIME LEFT'
            pos: status.x + status.width/4 * 3, status.y
            
        GenLabel:
            id: timerData
            text: '-'
            pos: status.x + status.width/4 *3 + 200, status.y
            
        GenLabel:
            id: title
            text: 'GENE SPLICER'
            pos: status.x + status.width/2.1, status.y
            font_size: 64
<Bottom>
    cols: 3
    id: bottomBox
    Div:
        id: temperature
        size: root.size
        pos: root.pos
        canvas:
            Color:
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
                size: (self.width*4)/6, self.height/6
                pos: self.width/6, self.height/1.2
        GenLabel:
            font_size: 56
            pos: temperature.width/2.4, temperature.height/1.25
            text: 'Temperature'
        GenLabel:
            id: tempInfo
            font_size: 116
            pos: temperature.width/2 - 45, temperature.height/4
            text: 'Waiting...'
        GenLabel:
            id: targetLabel
            pos: temperature.width/3, temperature.height/2
            text: 'Target:'
        GenLabel:
            id: targetData
            pos: temperature.width/1.75, temperature.height/2
            text: '100 C'
    Div:
        id: pressure
        size: root.size
        pos: root.pos
        canvas:
            Color:
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
                size: (((root.width*4)/6)/3), self.height/6
                pos: ((root.width/3)+(root.width/18)), self.height/1.2
        GenLabel:
            font_size: 64
            pos: 920, root.height/1.225
            text: 'Pressure'
        GenLabel:
            id: pressInfo
            font_size: 116
            pos: 920, root.height/4
            text: 'Waiting...'
        GenLabel:
            id: targetLabel
            pos: 800, root.height/2
            text: 'Target:'
        GenLabel:
            id: targetData
            pos: 995, root.height/2
            text: '9.17 Atm'
                
    Div:
        id: voltage
        size: root.size
        pos: root.pos
        canvas:
            Color:
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
            font_size: 64
            pos: 1550, root.height/1.225
            text: 'Voltage'
        GenLabel:
            id: voltInfo
            font_size: 116
            pos: 1550, root.height/4
            text: 'Waiting...'
        GenLabel:
            id: targetLabel
            pos: 1500, root.height/2
            text: 'Target:'
        GenLabel:
            id: targetData
            pos: 1650, root.height/2
            text: '32V'
'''

Builder.load_string(kv)
portCom = 'COM3'
portBut = 'COM4'
serCom = serial.Serial(portCom, baudrate=9600, timeout = 0)
serBut = serial.Serial(portBut, baudrate = 19200, timeout = 0)
serCom.flush()
serBut.flush()
sioCom = io.TextIOWrapper(io.BufferedRWPair(serCom,serCom), newline='\r\n', encoding = 'utf-8')
sioBut = io.TextIOWrapper(io.BufferedRWPair(serBut,serBut), newline='\r\n', encoding = 'utf-8')

#needed to give enough time for the port to initiate
time.sleep(3)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    #only HTTP request needed, sent by EscapeRoomMaster
    def do_GET(self):
        app = App.get_running_app()
        self._set_headers()

#seperate thread is made to manage all network requests, class shouldn't need to be changed
class Server(socketserver.ThreadingMixIn, HTTPServer):
    def process_requests(self, *args):
        while(True):
            self.handle_request()

def buttonTrig():
    app = App.get_running_app()
    while True:
        status = sioBut.readline()
        if ('1' in status):
            app.instance.children[1].ids.catalyst.jump()

class Cata(FloatLayout):
    puzzleSolved = False
    gravity = 0.05
    velocity = 0
    accel = 0
    close = BooleanProperty(False)
    points = ListProperty([28,850,28,850])
    meshPointsBot = [50,655,0,0, 321,875,0,0, 640,850,0,0, 960,950,0,0, 1280,950,0,0, 1600,800,0,0, 1895,700,0,0, 1895,655,0,0]
    meshBotCollide = Collide2DPoly([float(x) for x in meshPointsBot if x != 0], cache=True)
    meshIndBot = [0,1,2,3,4,5,6,7]
    meshPointsTop = [50,1055,0,0, 321,955,0,0, 640,955,0,0, 960,1000,0,0, 1280,1030,0,0, 1600,975,0,0, 1895,750,0,0, 1895,1055,0,0, 960,1055,0,0, 640,1055,0,0]
    meshTopCollide = Collide2DPoly([50,1055, 321,955, 640,955, 960,1000, 1005,1000, 1380,985, 1895,750, 1895,1055, 50,1055])
    meshIndTop = [0,1,2,3,4,5,6,7,5,8,9,1,7,0]
    counter = 0
    crossed = [False, False, False, False, False]
    linewidth = NumericProperty(3)
    nextPoint = 321
    prevPoint = 28
    def __init__(self, **kwargs):
        super(Cata, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def update_points(self, *args):
        app = self.app
        temp = []
        temp.append(self.points.pop())
        temp.append(self.points.pop())
        if (app.started):
            if ((float(temp[1]), float(temp[0])) in self.meshBotCollide or (float(temp[1]), float(temp[0])) in self.meshTopCollide):
                app.reset()
                return
            #timer data, proportion of distance crossed
            if (not self.puzzleSolved):
                timerData = ((self.nextPoint - round(temp[1],1))) / ((self.nextPoint - self.prevPoint) / 10)
                app.root.children[1].ids.timerData.text = ('%.2f' % round(timerData,2))
                if (timerData < 3):
                    app.root.children[1].ids.timerData.color = (1,0,0,1)
                    app.stageCheck(temp[1])
                else:
                    app.root.children[1].ids.timerData.color = (1,1,1,1)
                    
        #acceleration per height region
        self.accel += self.gravity
        toCheck = self.accel
        if (toCheck < 3.5 and toCheck > 0): 
            self.accel *= 1.2
        elif (toCheck < 0):
            self.accel *= 0.8
        elif (toCheck == 0):
            self.accel = 0.5

        self.velocity += self.accel

        if (app.started):
            ######
            #constant x movement for different sections. first and last are smaller than the rest
            if (not self.crossed[0]):
                temp[1] += .81 #.54
            elif (not self.crossed[4]):
                temp[1] += .81 #.54 .5316
            elif (self.crossed[0] and self.crossed[4]):
                temp[1] += .81 #.4883
            ######

        self.points.append(temp[1])
        temp[0] -= self.velocity
        if (temp[0] > 1050):
            temp[0] = 1050
        elif (temp[0] < 660):
            temp[0] = 660
        temp[0] = round(temp[0], 1)
        self.points.append(temp[0])
        
        if (self.velocity > 0):
            self.velocity = 0
        
        if (app.started):
            ######
            if (self.counter == 20):
                self.points.append(temp[1])
                self.points.append(temp[0])
                self.counter = 0
            else:
                self.counter += 1
            ######
            
    def jump(self, *args):
        currentAccel = self.accel
        toCheck = self.points[-1]
        if (toCheck > 975 and not currentAccel == -0.21):
            self.accel = -0.21
        elif(toCheck > 860 and not currentAccel == -0.25) :
            self.accel = -0.25
        elif(toCheck > 800 and not currentAccel == -0.35):
            self.accel = -0.35
        elif(not currentAccel == -0.5):
            self.accel = -0.5
class Top(GridLayout):
    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)
class Bottom(GridLayout):
    def __init__(self, **kwargs):
        super(Bottom, self).__init__(**kwargs)
class Div(Widget):
    def __init__(self, **kwargs):
        super(Div, self).__init__(**kwargs)

    def generateTarget(self, *args):
        app = App.get_running_app()
        if ("range" in args):
            self.target1 = random.randint(10,97)
            self.target2 = self.target1 + 2
            self.children[0].text = str(self.target1) + "-" + str(self.target2) 
        else:
            self.target1 = random.randint(10,99)
            self.children[0].text = str(self.target1)
        
class Base(GridLayout):
    def __init__(self, **kwargs):
        super(Base, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        print(touch.pos)
        
class GenLabel(Label):
    def __init__(self, **kwargs):
        self.font_name = 'ColdWarm.otf'
        self.font_size = 48
        super(GenLabel, self).__init__(**kwargs)
        
class SpliceApp(App):
    prevData = ""
    started = False
    wonLabel = InstructionGroup()
    tempTargets = [100, 152, 405, 385, 275, 36]
    voltTargets = [32, 7, 24, 228, 255, 4]
    presTargets = [9.17, 8.65, 7.21, 7., 2.07, 2.35]
    tempCurrent = 0
    voltCurrent = 0
    presCurrent = 0

    def __init__(self, **kwargs):
        self.serRead = Clock.schedule_interval(self.serialRead, 0.05)
        super(SpliceApp, self).__init__(**kwargs)
        
    def serialRead(self, *args):
        data = self.getLatestStatus()
        if (not data):
            return
        self.prevData = data
        del data[0]
        del data[-1]
        while(len(data) >= 2):
            if (data[0] == 'P'):
                textToSet = str(round(float(data[1]), 2))
                self.instance.children[0].ids.tempInfo.text = textToSet
            elif(data[0] == 'W' and not self.started):
                if (str(data[1]) == 'True'):
                    self.started = True
                    #self.update = Clock.schedule_interval(self.instance.children[1].ids.catalyst.update_points, .016)
            elif(data[0] == 'R'):
                if (float(data[1]) < 0):
                    textToSet = "0.000"
                else:
                    textToSet = str(float(data[1])).ljust(5, '0')
                self.instance.children[0].ids.pressInfo.text = textToSet
            elif(data[0] == 'V'):
                textToSet = str(data[1])
                self.instance.children[0].ids.voltInfo.text = textToSet
            del data[0:1]
    def stageCheck(self, *args):
        temp = args[0]
        cata = self.instance.children[1].ids.catalyst

        if (not cata.crossed[0] and temp >= 321):
            cata.prevPoint = 321
            cata.nextPoint = 640
            cata.crossed[0] = True
            cata.canvas.get_group("coverColor")[0].rgba = [0,0,0,0]
            self.instance.children[1].ids.statusText.text = 'STAGE 2 OF 6'
            self.instance.children[0].ids.temperature.children[0].text = str(self.tempTargets[1]) + " C"
            self.instance.children[0].ids.pressure.children[0].text = str(self.presTargets[1]) + " ATM"
            self.instance.children[0].ids.voltage.children[0].text = str(self.voltTargets[1]) + "V"
        elif(not cata.crossed[1] and temp >= 640):
            cata.prevPoint = 640
            cata.nextPoint = 959
            cata.crossed[1] = True
            cata.canvas.get_group("coverColor")[1].rgba = [0,0,0,0]
            self.instance.children[1].ids.statusText.text = 'STAGE 3 OF 6'
            self.instance.children[0].ids.temperature.children[0].text = str(self.tempTargets[2]) + " C"
            self.instance.children[0].ids.pressure.children[0].text = str(self.presTargets[2]) + " ATM"
            self.instance.children[0].ids.voltage.children[0].text = str(self.voltTargets[2]) + "V"
        elif(not cata.crossed[2] and temp >= 959):
            cata.prevPoint = 959
            cata.nextPoint = 1280
            cata.crossed[2] = True
            cata.canvas.get_group("coverColor")[2].rgba = [0,0,0,0]
            self.instance.children[1].ids.statusText.text = 'STAGE 4 OF 6'
            self.instance.children[0].ids.temperature.children[0].text = str(self.tempTargets[3]) + " C"
            self.instance.children[0].ids.pressure.children[0].text = str(self.presTargets[3]) + " ATM"
            self.instance.children[0].ids.voltage.children[0].text = str(self.voltTargets[3]) + "V"
        elif(not cata.crossed[3] and temp >= 1280):
            cata.prevPoint = 1280
            cata.nextPoint = 1600
            cata.crossed[3] = True
            cata.canvas.get_group("coverColor")[3].rgba = [0,0,0,0]
            self.instance.children[1].ids.statusText.text = 'STAGE 5 OF 6'
            self.instance.children[0].ids.temperature.children[0].text = str(self.tempTargets[4]) + " C"
            self.instance.children[0].ids.pressure.children[0].text = str(self.presTargets[4]) + " ATM"
            self.instance.children[0].ids.voltage.children[0].text = str(self.voltTargets[4]) + "V"
        elif(not cata.crossed[4] and temp >= 1600):
            cata.prevPoint = 1600
            cata.nextPoint = 1892
            cata.crossed[4] = True
            cata.canvas.get_group("coverColor")[4].rgba = [0,0,0,0]
            self.instance.children[1].ids.statusText.text = 'STAGE 6 OF 6'
            self.instance.children[0].ids.temperature.children[0].text = str(self.tempTargets[5]) + " C"
            self.instance.children[0].ids.pressure.children[0].text = str(self.presTargets[5]) + " ATM"
            self.instance.children[0].ids.voltage.children[0].text = str(self.voltTargets[5]) + "V"
        elif(temp >= 1892):
            cata.puzzleSolved = True
            self.instance.children[1].ids.timerData.text = ('%.2f' % 0.0)
            Clock.unschedule(self.update)
            self.win()
       
    def build(self):
        self.instance = Base()
        won = self.wonLabel
        won.add(Color(0,0,0,1))
        won.add(Rectangle(size=(1000, 190), pos= (400, 520)))
        won.add(Color(0,1,0,1))
        won.add(Rectangle(size=(980, 210), pos= (410, 530)))
        won.add(Color(1,1,1,1))
        label = CoreLabel(font_size=64, font_name='basica.ttf', text = 'SPLICING COMPLETE')
        label.refresh()
        won.add(Rectangle(texture=label.texture, size= label.size, pos=(475, 600)))
        self.update = Clock.schedule_interval(self.instance.children[1].ids.catalyst.update_points, .016)
        self.buttonThread = threading.Thread(target = buttonTrig).start()
        return self.instance

    def getLatestStatus(self, *args):
        valid = False
        status = sioCom.readline()
        while serCom.inWaiting() > 0:
            status = sioCom.readline()
        if('W' in status and not self.started):
                status = "S-W-True-E"
                serCom.write(b'K\r\n')
                self.started = True
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
        self.prevData = ""
        cata = self.instance.children[1].ids.catalyst
        cata.points.clear()
        cata.points = [28,850,28,850]
        
        self.instance.children[1].ids.timerData.color = (1,1,1,1)
        self.instance.children[1].ids.timerData.text = "-"
        self.instance.children[1].ids.statusText.text = 'STAGE 1 OF 6'

        cata.gravity = 0.05
        cata.velocity = 0
        cata.accel = 0
        cata.nextPoint = 321
        cata.prevPoint = 28
        #reset cata covers
        cata.crossed = [False, False, False, False, False]
        for x in cata.canvas.get_group('coverColor'):
            x.rgba = 0,0,0,1
        
        #serial commune stopped
        serCom.write(b'R\r\n')
        #reset individual component labels
        #self.instance.
        temp = self.instance.children[0].ids.temperature
        pres = self.instance.children[0].ids.pressure
        volt = self.instance.children[0].ids.voltage
        temp.children[0].text = str(self.tempTargets[0]) + " C"
        pres.children[0].text = str(self.presTargets[0]) + " ATM"
        volt.children[0].text = str(self.voltTargets[0]) + "V"

        
    def win(self, *args):
        self.instance.canvas.add(self.wonLabel)

def serverRun(server_class=Server, handler_class=Handler, port=80):
    server_address = ('10.24.7.62', port)
    httpd = server_class(server_address, handler_class)
    print("serving at port",port)
    t = threading.Thread(target = httpd.process_requests)
    t.start()
    
if __name__ == '__main__':
    serverRun()
    SpliceApp().run()
