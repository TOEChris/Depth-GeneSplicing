
import gaugette.gpio
import gaugette.switch as CS
import threading

gpio = gaugette.gpio.GPIO()
cataButton = CS.Switch(gpio, 0)

while True:
    if(cataButton.get_state()):
        print("gottem")
