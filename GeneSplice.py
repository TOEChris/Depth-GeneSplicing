from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import OptionProperty, NumericProperty, ListProperty, BooleanProperty

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
from kivy.uix.button import Button

import time
import wiringpi
import serial
import gaugette.gpio
import gaugette.switch as CS
from functools import partial
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import socketserver

gpio = gaugette.gpio.GPIO()
cataButton = CS.Switch(gpio, 0)

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
            Mesh:
                mode: 'triangle_fan'
                vertices: self.meshPoints
                indices: self.meshInd
                texture: 
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
                rgba: 0,0,0,1
            Rectangle:
                group:'cover'
                size: self.width/6-5, self.height-50
                pos: self.width/6+5, self.y+25
            Rectangle:
                group:'cover'
                size: self.width/6-5, self.height-50
                pos: self.width/6*2+5, self.y+25
            Rectangle:
                group:'cover'
                size: self.width/6-5, self.height-50
                pos: self.width/6*3+5, self.y+25
            Rectangle:
                group:'cover'
                size: self.width/6-5, self.height-50
                pos: self.width/6*4+5, self.y+25
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
            text: 'STAGE 1 OF 6'
            pos: status.x + status.width/6, status.y

        GenLabel:
            id: timer
            text: 'TIME LEFT'
            pos: status.x + status.width/4 * 3, status.y
            
        GenLabel:
            id: timerData
            text: '10.0'
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
            id: tempInfo
            font_size: 116
            pos: temperature.width/2 - 45, temperature.height/4
            text: 'Waiting...'
        GenLabel:
            font_size: 56
            pos: temperature.width/2.4, temperature.height/1.25
            text: 'Temperature'
        GenLabel:
            id: targetLabel
            pos: temperature.width/3, temperature.height/2
            text: 'Target:'
        GenLabel:
            id: targetData
            pos: temperature.width/1.75, temperature.height/2
            text: '-'
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
            id: pressLabel
            pos: 850, root.height/2
            text: 'Target:'
        GenLabel:
            id: pressData
            pos: 1000, root.height/2
            text: '-'
                
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
'''

Builder.load_string(kv)
file = open("results.txt","w")
port = '/dev/ttyACM0'
ser = serial.Serial(port, baudrate=9600, timeout = 0);

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
    counter = 0
    app = App.get_running_app()
    while True:
        if (cataButton.get_state()):
            app.instance.children[1].ids.catalyst.jump()
            while cataButton.get_state():
                pass

class Cata(FloatLayout):
    endPuzzle = False
    startTime = 0
    gravity = 0.05
    velocity = 0
    accel = 0
    accelChange = True
    close = BooleanProperty(False)
    points = ListProperty([28,850,28,850])
    meshPoints = ListProperty([100,100,0,0, 150,500,0,0, 1,2,0,0, 2,1,0,0, 2,2,0,0, 4,4,0,0, 5,2,0,0])
    meshInd = [0,1,2,3,4,5,6]
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
        
        #timer data, proportion of distance crossed
        if (not self.endPuzzle):
            timerData = ((self.nextPoint - round(temp[1],1))) / ((self.nextPoint - self.prevPoint) / 10)
            app.root.children[1].ids.timerData.text = ('%.2f' % round(timerData,2))
            if (timerData < 3 and not app.root.children[1].ids.timerData.color == (1,0,0)):
                app.root.children[1].ids.timerData.color = (1,0,0)
            else:
                app.root.children[1].ids.timerData.color = (1,1,1)
                    
        self.accelChange = False
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
        self.accelChange = True
        #constant x movement for different sections. first and last are smaller than the rest
        if (not self.crossed[0]):
            temp[1] += .54 #.5125
        elif (not self.crossed[4]):
            temp[1] += .54 #.54 .5316
        elif (self.crossed[0] and self.crossed[4]):
            temp[1] += .5 #.4883
        
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
        
        
        if (not self.crossed[0] and self.points[-2] >= 321):
            self.prevPoint = 321
            self.nextPoint = 640
            self.crossed[0] = True
            self.canvas.remove(self.canvas.get_group('cover')[0])
            app.root.children[1].ids.statusText.text = 'STAGE 2 OF 6'
        elif(not self.crossed[1] and self.points[-2] >= 640):
            self.prevPoint = 640
            self.nextPoint = 959
            self.crossed[1] = True
            self.canvas.remove(self.canvas.get_group('cover')[0])
            app.root.children[1].ids.statusText.text = 'STAGE 3 OF 6'
        elif(not self.crossed[2] and self.points[-2] >= 959):
            self.prevPoint = 959
            self.nextPoint = 1280
            self.crossed[2] = True
            self.canvas.remove(self.canvas.get_group('cover')[0])
            app.root.children[1].ids.statusText.text = 'STAGE 4 OF 6'
        elif(not self.crossed[3] and self.points[-2] >= 1280):
            self.prevPoint = 1280
            self.nextPoint = 1600
            self.crossed[3] = True
            self.canvas.remove(self.canvas.get_group('cover')[0])
            app.root.children[1].ids.statusText.text = 'STAGE 5 OF 6'
        elif(not self.crossed[4] and self.points[-2] >= 1600):
            self.prevPoint = 1600
            self.nextPoint = 1892
            self.crossed[4] = True
            self.canvas.remove(self.canvas.get_group('cover')[0])
            self.canvas.remove(self.canvas.get_group('cover')[0])
            app.root.children[1].ids.statusText.text = 'STAGE 6 OF 6'
        elif(self.points[-2] >= 1892):
            self.endPuzzle = True
            app.root.children[1].ids.timerData.text = ('%.2f' % 0.0)
            Clock.unschedule(app.update)

        if (self.counter == 20):
            self.points.append(temp[1])
            self.points.append(temp[0])
            self.counter = 0
        else:
            self.counter += 1
            
    def jump(self, *args):
        if (not self.accelChange):
            return
        currentAccel = self.accel
        toCheck = self.points[-1]
        if (toCheck > 975 and not currentAccel == -0.3):
            self.accel = -0.3
        elif(toCheck > 860 and not currentAccel == -0.35) :
            self.accel = -0.35
        elif(toCheck > 800 and not currentAccel == -0.4):
            self.accel = -0.4
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
class Base(GridLayout):
    def __init__(self, **kwargs):
        super(Base, self).__init__(**kwargs)
class GenLabel(Label):
    def __init__(self, **kwargs):
        self.font_name = 'ColdWarm.otf'
        self.font_size = 48
        super(GenLabel, self).__init__(**kwargs)
        
class SpliceApp(App):
    def __init__(self, **kwargs):
        self.event = Clock.schedule_interval(self.serialRead, 0.20)
        super(SpliceApp, self).__init__(**kwargs)
        
    def serialRead(self, *args):
        data = self.getLatestStatus().decode('ascii').split("-")
        app = App.get_running_app()
        while(len(data) >= 2):
            if (data[0] == 'P'):
                try:
                    textToSet = str(round(float(data[1]), 2))
                    self.instance.children[0].ids.tempInfo.text = textToSet
                except Exception:
                    pass
                del data[0:1]
            elif(data[0] == 'S'):
                if (str(data[1]) == 'True'):
                    self.buttonThread = threading.Thread(target = buttonTrig).start()
                    self.update = Clock.schedule_interval(self.instance.children[1].ids.catalyst.update_points, .016)
                del data[0:1]
            elif(data[0] == 'R'):
                try:
                    if (float(data[1]) < 0):
                        textToSet = "0"
                    else:
                        textToSet = str(round(float(data[1]), 2))
                    self.instance.children[0].ids.pressInfo.text = textToSet
                except Exception:
                    pass
                del data[0:1]
            
       
    def build(self):
        self.instance = Base()
        #indicates to Arduino to start sending data
        #ser.write(b'Z\r\n')
        return self.instance

    def getLatestStatus(self, *args):
        status = ser.readline()
        while ser.inWaiting() > 0:
            status = ser.readline()
        return status

def serverRun(server_class=Server, handler_class=Handler, port=80):
    server_address = ('10.24.7.15', port)
    httpd = server_class(server_address, handler_class)
    print("serving at port",port)
    t = threading.Thread(target = httpd.process_requests)
    t.start()
    
if __name__ == '__main__':
    #serverRun()
    SpliceApp().run()
