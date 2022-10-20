# Coded by Tea S.
# 2022 
from random import randint
import math
from machine import Pin, I2C,PWM,freq,reset
from ssd1306 import SSD1306_I2C
import utime
import neopixel
import framebuf
import os
import json
from sys import exit

# Overlock pico to max cpu freq
freq(240000000)
# PIN CONFIGURATION

# Setup screen connection over I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=2200000)
display = SSD1306_I2C(128, 64, i2c)


# Hardcoded config file for if it doesnt exist on the pico
config = {'vibrationMotor': {'pin': 27}, 'state': 'Closed', 'buttons': {'cooldown': {'pin': 21}, 'fire': {'pin': 21}, 'reload': {'pin': 21}, 'screen': {'pin': 21}}, 'colors': {'reloading': [[0, 255, 0], [0, 0, 0]], 'cooldown': [[155, 135, 135], [255, 255, 255]], 'normal': [[225, 0, 0], [15, 15, 15]], 'flash': [[255, 25, 25], [15, 15, 15]]}, 'lights': {'toplight': {'length': 18, 'pin': 4, 'flicker': True}, 'maglight': {'length': 9, 'pin': 17, 'flicker': False}, 'barrelled': {'pin': 22}}, 'servos': {'barrelEnd': {'pin': 19, 'start': 23, 'speed': 15, 'invert': True, 'end': 75, 'curpos': 23}, 'top1': {'pin': 21, 'start': 20, 'speed': 100, 'invert': True, 'end': 156, 'curpos': 20}, 'barrel': {'pin': 18, 'start': 26, 'speed': 100, 'invert': False, 'end': 52, 'curpos': 26}, 'screen': {'pin': 26, 'start': 2, 'speed': 100, 'invert': False, 'end': 58, 'curpos': 58}, 'top2': {'pin': 20, 'start': 20, 'speed': 100, 'invert': True, 'end': 149, 'curpos': 20}, 'top3': {'pin': 28, 'start': 20, 'speed': 100, 'invert': True, 'end': 160, 'curpos': 20}}}


# Load config file from system (it holds all the servo settings and current position so the servos dont judder when it turns back on)
if "config" in os.listdir():
    try:
        file = open("config", "r")
        config = json.loads(file.readline())
        file.close()
    except ValueError:
        # Problem reading config file, recreate it using the above hardcoded config file
        print("Unable to read config file...Recreating")
        file = open("config", "wb")
        file.write(json.dumps(config))
        file.close()
else:
    # Create config file if it doesn't exist
    file = open("config", "wb")
    file.write(json.dumps(config))
    file.close()


def saveSettings():
    file = open("config", "wb")
    file.write(json.dumps(config))
    file.close()


# Oddworks logo
def get_img():
    img = bytearray(b'BM>\x04\x00\x00\x00\x00\x00\x00>\x00\x00\x00(\x00\x00\x00\x80\x00\x00\x00@\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x04\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xee\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xcd\xc4<\x00\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xf9F4\xc0\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x029Fe\xe0\x03\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01g\xc7 \xe60\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xe3c\xce>\xf6\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?0\x0e?\xb6\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c0\x1eq\x9e\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf06\xe1\x8c\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00f\xc1\x80\x98\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x00\xc6\xdd\x81\xcc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xc1\x84\xd9\xb0\xce\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1eG\xcc\xc1\xb8\xe7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\xfc\xc38\xa3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x9b\x1c\xff<\xf1\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07#\x00\xbf4\xd1\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\'\xf8\x826\xd8\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18{\xfd\x82"\xc8\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\xe0\xcd\xb2c\xfc\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\xdee\xff\xcf\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\xbf\'\xc7\x1f\x1f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xb1\xb3\x81\xb8\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e\xa0\xd6\x18\xb1\xc3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xde|\xe3\xf1\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xa0\x9c\xec\xe61\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x9b\x9c\x86D\x19\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x1f\x1c\x86\xc6\x19\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x008\xcc\xe3s\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00xy\xf3\xe3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\xcc\x03\xb8\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x07\x8c\x0f\x1c\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x87\x0c>\x0f\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc6\x040\x03\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00v\x06 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\x060\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x848\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x8c\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\xcc\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10M\x8c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00pO\xcc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc0O\xce\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x04FF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x0e\xc0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x1b\x80F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04;\x80\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xf0\x00\xc2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x01\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\xe6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xe6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    img = bytearray([img[ii] for ii in range(len(img)-1,-1,-1)])
    img_res = (128,64)
    return img,img_res
    


print(config)
# ===========================START OF CLASSES ==================================

# Class for controlling and setting servo settings, pass in a config file with all the settings of the servo
class Servo:
    def __init__(self,config):
        self.speed = config['speed']
        self.posMin = config['start']
        self.posMax = config['end']
        self.pin = config['pin']
        self.invert = config['invert']
        self.config = config

        self.targetAngle = config['curpos']
        self.angle = config['curpos']
        self.pwm = PWM(Pin(self.pin, Pin.OUT))
        self.pwm.freq(50)
    def setPos(self,angle):
        if not self.isMoving():
            if round(angle) != round(self.angle):
                if angle > self.posMax:
                    angle = self.posMax
                elif angle < self.posMin:
                    angle = self.posMin
                self.targetAngle = angle
                # save angle to config file here
                self.saveCurPos()
    def setMin(self,min):
        self.posMin = min
        self.setPos(min)
    def setMax(self,max):
        self.posMax = max
        self.setPos(max)
    def setSpeed(self,speed):
        if speed != self.speed:
            self.speed = speed
    def getSpeed(self):
        return self.speed
    def setInvert(self,invert):
        self.invert = invert
    def update(self):
        if self.angle < self.targetAngle:
            self.angle += (self.speed / 100)
        elif self.angle > self.targetAngle:
            self.angle -= (self.speed / 100)
        self.moveServo(int(self.angle))

    def moveServo(self, degrees):
        # limit degrees between 0 and 180
        if degrees > 180:
            degrees = 180
        if degrees < 0:
            degrees = 0
        if self.invert:
            degrees = (180 + 0) - degrees
        # set max and min duty
        maxDuty = 9000
        minDuty = 1500
        # new duty is between min and max duty in proportion to its value
        newDuty = minDuty + (maxDuty - minDuty) * (degrees / 180)
        # servo PWM value is set
        self.pwm.duty_u16(int(newDuty))

    def isMoving(self):
        if round(self.angle) == round(self.targetAngle):
            return False
        else:
            return True

    def open(self):
        self.setPos(self.posMax)

    def close(self):
        self.setPos(self.posMin)
        # Need to improve this, only works if the servo was set using open() or close()
    def toggle(self):
        if round(self.angle) == round(self.posMax):
            self.close()
        if round(self.angle) == round(self.posMin):
            self.open()
    def saveCurPos(self):
        self.config['curpos'] = self.targetAngle
        saveSettings()
# Class for displaying progress bars on the screen, the progress bar can have a min, max, label and other settings for size etc
class ProgressBar:
    def __init__(self,amount,position,height,label,min=0,max=100):
        self.amount = amount
        self.position = position
        self.height = height
        self.label = label
        self.min = min
        self.max = max
        # If position is auto, automatically calculate the y position based on the previously created bar in the list of bars
        if self.position['y'] == 'auto':
            try:
                if bars[-1]:
                    self.position['y'] = bars[-1].position['y'] + bars[-1].height + 10
            except IndexError:
                # list of bars doesn't exist, set the y to 0
                self.position['y'] = 0
                pass
    def update(self):
        display.rect(self.position['x'],self.position['y'],128,self.height,1)
        display.fill_rect(self.position['x'],self.position['y'],int(128 * self.amount / self.max),self.height,1)
        toDisplay = self.label + " " + str(self.amount)
        display.text(toDisplay,int(self.position['x'] + 128 / 2) - (len(toDisplay) * 4), self.position['y'] + self.height + 1,1)
    def setAmount(self,amount):
        amount = int(amount)
        if amount >= self.min and amount <= self.max:
            self.amount = amount
#Pixel class based on RGB tuples, capable of animation from one colour to another, adjusting brightness as a whole and enabling a cool flicker effect (possibly more in the future)
class Pixel:
    def __init__(self, speed, brightness, color, flicker=True):
        # Normal Flicker
        self.brightness = 0
        self.color = list(color[0])
        self.flashColor = list(color[1])

        self.targetColor = list(color[0])
        self.targetFlashColor = list(color[1])

        self.randomFlicker = randint(int(1 * speed),int(20 * speed))
        self.speed = speed
        self.randomFlickerCount = 0
        self.randomFlickerOn = 0
        self.brightnessNormal = 0
        self.brightnessFlicker = 0
        self.animationSpeed = 1
        self.isFlicker = flicker
        self.animating = False
        self.setBrightness(brightness)
    def getPixelState(self):
        self.randomFlickerCount += 1
        self.randomFlickerOn -= 1
        if self.randomFlickerCount >= self.randomFlicker:
            self.randomFlicker = randint(int(1 * self.speed), int(20 * self.speed))
            self.randomFlickerOn = 1
            self.randomFlickerCount = 0
        if self.randomFlickerOn > 0 and self.isFlicker:
            return tuple([int(x * self.brightness / 100) for x in self.flashColor])
        else:
            return tuple([int(x * self.brightness / 100) for x in self.color])
    def update(self):
        # Handle colour animation
        if self.color != self.targetColor:
            for i in range(len(self.color)):
                if self.color[i] > self.targetColor[i]:
                    self.color[i] = self.color[i] - self.animationSpeed
                if self.color[i] < self.targetColor[i]:
                    self.color[i] = self.color[i] + self.animationSpeed
                if self.flashColor[i] > self.targetFlashColor[i]:
                    self.flashColor[i] = self.flashColor[i] - self.animationSpeed
                if self.flashColor[i] < self.targetFlashColor[i]:
                    self.flashColor[i] = self.flashColor[i] + self.animationSpeed

        #Handle random flickering effect
        return self.getPixelState()
    # Get rgb tuple for writing to neopixels
    def getRgb(self):
        return self.rgbCurrent
    def isAnimating(self):
        return self.animatng
    # Set the color to animate to
    def animateColor(self,color, speed=0):
        if speed != 0:
            self.animationSpeed = speed
        self.targetColor = list(color[0])
        self.targetFlashColor = list(color[1])
    def setColor(self,color):
        self.targetColor = list(color[0])
        self.targetFlashColor = list(color[1])
        self.color = list(color[0])
        self.flashColor = list(color[1])

    def setAnimationSpeed(self,speed):
        self.animationSpeed = speed
    def setBrightness(self,brightness):
        if self.brightness != brightness:
            if brightness > 100:
                brightness = 100
            elif brightness <= 0:
                brightness = 0
            self.brightness = brightness
    def setFlicker(self,flicker):
        self.isFlicker = flicker
# Class for handling neolight lighting (just holds individual pixels and updates them all the logic happens in the pixel class above)
class NeoLight:
    def __init__(self, config):
        self.config = config
        self.brightness = 0
        self.pin = config['pin']
        self.cooldown = False
        self.speed = 1
        self.length = config['length']
        self.np = neopixel.NeoPixel(Pin(config['pin']),config['length'])
        self.pixels = []
        self.color = [[225, 0, 0], [15, 15, 15]]
        self.cooldown = False
        self.flicker = config['flicker']
        for i in range(len(self.np)):
            pixel = Pixel(self.speed,self.brightness,self.color,self.flicker)
            self.pixels.append(pixel)
    def update(self):
        for index,pixel in enumerate(self.pixels):
            self.np[index] = pixel.update()
        self.np.write()
    def animateColor(self,color, speed=0):
        if color != self.color:
            for pixel in self.pixels:
                if speed > 0:
                    pixel.animateColor(color,speed)
                else:
                    pixel.animateColor(color)
            self.color = color
    def setColor(self,color):
        if self.color != color:
            for pixel in self.pixels:
                pixel.setColor(color)
                self.color = color
    def setBrightness(self,brightness):
        if self.brightness != brightness:
            if brightness > 100:
                brightness = 100
            elif brightness < 0:
                brightness = 0
            for pixel in self.pixels:
                pixel.setBrightness(brightness)

            self.brightness = brightness
    def setFlicker(self,flicker):
        self.flicker = flicker
# Class for handling input buttons, you can set if it should fire off once or press and hold to continually output true after a predefined timeout.
class Button:
    def __init__(self, pin, single=False):
        self.single = single
        self.pin = pin
        self.lock = False
        self.button = Pin(pin,Pin.IN, Pin.PULL_DOWN)
        self.timeout = 5
        self.interval = 5
        self.count = 0
        self.held = False
    def getState(self, single=True):
        if self.button.value():
            self.held = True
            if not self.lock:
                self.lock = True
                return True
            else:
                if not single:
                    if self.count >= self.timeout:
                        self.lock = False
                        pass
                    self.count = self.count + 1
                return False
        else:
            self.lock = False
            self.count = 0
            self.held = False
            return False
    def getHeld(self):
        return self.held
# Basic timer class to count down things and call a method when it reaches its goal
class Timer:
    def __init__(self,start,end,interval,functions=[]):
        self.end = end
        self.start = start
        self.current = start
        self.interval = interval
        self.functions = functions
    def update(self,do):
        if do:
            if self.interval > 0:
                if self.current <= self.end:
                    self.current = self.current + self.interval
            else:
                if self.current >= self.start:
                    self.current = self.current + self.interval
        if self.current >= self.end:
            for function in self.functions:
                if callable(function):
                    function()
            return True
        else:
            return False

    def reset(self):
        self.current = self.start
    def getState(self):
        return self.current
    def setStartEnd(self,start,end):
        self.start = start
        self.end = end
# Base class all options extend
class Option:
    def __init__(self,x,y,label,selected):
        self.selected = selected
        self.label = label
        self.label2 = ""
        self.x = x
        self.y = y
        self.height = 12
        self.editing = False
        self.blink = 1
        self.count = 10
    def updateDisplay(self):
        if not self.editing:
            if self.selected:
                display.fill_rect(self.x,self.y,128,self.height,1)
                display.text(str(self.label),self.x + 1,self.y + 2,0)
                display.text(str(self.label2),128 - (len(self.label2) * 8),self.y + 2,0)
            else:
                display.text(str(self.label),self.x + 1,self.y + 2,1)
                display.text(str(self.label2),128 - (len(self.label2) * 8),self.y + 2,1)
        else:
            display.fill_rect(128 - (len(self.label2) * 8),self.y,128,self.height,self.blink)
            display.text(str(self.label),self.x + 1,self.y + 2,1)
            display.text(str(self.label2),128 - (len(self.label2) * 8),self.y + 2,not self.blink)
            if self.count < 0:
                self.count = 10
                self.blink = not self.blink
            self.count = self.count - 1
    def update(self):
        pass
    def getValue(self):
        pass
    def setSelected(self,selected):
        self.selected = selected
    def getSelected(self):
        return self.selected
    def setEditing(self,editing):
        self.editing = editing
    def getEditing(self):
        return self.editing
    def setLabel2(self,label):
        self.label2 = label
    def getName(self):
        return type(self).__name__
# An option for setting an int value, interval and kept between a min and max
class numberOption(Option):
    def __init__(self, x, y,label,selected,valueMin,valueMax,interval,start,func=None):
        super().__init__(x, y,label,selected)
        self.valueMin = valueMin
        self.valueMax = valueMax
        self.currentValue = start
        self.interval = interval
        self.setLabel2(str(self.currentValue))
        self.func = func
    def checkButtons(self):
        if self.editing:
            if cooldownBtn.getState(False):
                if self.currentValue < self.valueMax:
                    self.currentValue = round(self.currentValue + self.interval,self.interval)
                self.setLabel2(str(self.currentValue))
            if openCloseBtn.getState(False):
                if self.currentValue > self.valueMin:
                    self.currentValue = round(self.currentValue - self.interval,self.interval)
                self.setLabel2(str(self.currentValue))
            if fireBtn.getState():
                self.setEditing(False)
            if callable(self.func):
                self.func(self.currentValue)
    def getValue(self):
        return self.currentValue
# An option for setting true or false
class boolOption(Option):
    def __init__(self, x, y,label,selected,value,func=None):
        super().__init__(x, y, label, selected)
        self.currentValue = value
        self.setLabel2(str(value))
        self.func = func
    def checkButtons(self):
        if self.editing:
            if cooldownBtn.getState():
                self.currentValue = not self.currentValue
            self.setLabel2(str(self.currentValue))
            if openCloseBtn.getState():
                self.currentValue = not self.currentValue
            self.setLabel2(str(self.currentValue))
            if fireBtn.getState():
                self.setEditing(False)
            if callable(self.func):
                self.func(self.currentValue)
    def getValue(self):
        return self.currentValue
# For a select option, hitting enter calls the one or two provided functions
class selectOption(Option):
    def __init__(self, x, y,label,selected,func=None, func2=None):
        super().__init__(x, y, label, selected)
        self.func = func
        self.func2 = func2
    def checkButtons(self):
        if self.editing:
            self.setEditing(False)
            if callable(self.func):
                self.func()
            if callable(self.func2):
                self.func2()
# A label that display text, isnt selectable by the buttons and has centered text
class labelOption:
    def __init__(self,x,y,label):
        self.label = label
        self.label2 = ""
        self.x = x
        self.y = y
        self.height = 12
    def updateDisplay(self):
        display.text(str(self.label),int(64 - (len(self.label) * 4)),self.y + 2,1)

    def update(self):
        pass
    def getValue(self):
        pass
    def setSelected(self,selected):
        self.selected = selected
    def getSelected(self):
        return False
    def setEditing(self,editing):
        self.editing = editing
    def getEditing(self):
        return False
    def setLabel2(self,label):
        self.label2 = label
    def getName(self):
        return type(self).__name__
    def checkButtons(self):
        pass
# Extends basic servo functionality but also implements display options and passing in of servo config / save settings
class servoSettings(Servo):
    def __init__(self,config=None,backFunc=None):
        # Get config from pass config variable
        super().__init__(config)
        self.config = config
        self.backFunc = backFunc
        self.displayOptions = Menu(False)
        self.displayOptions.addOption(labelOption(0,0,"Servo Settings"))
        self.displayOptions.addOption(numberOption(0,12,"Start Pos",True,0,180,1,self.posMin,self.setMin))
        self.displayOptions.addOption(numberOption(0,24,"End Pos",False,0,180,1,self.posMax,self.setMax))
        self.displayOptions.addOption(numberOption(0,36,"Pin",False,1,30,1,self.pin))
        self.displayOptions.addOption(boolOption(0,48,"Invert",False,self.invert,self.setInvert))
        self.displayOptions.addOption(labelOption(0,0,"Servo Settings"))
        self.displayOptions.addOption(numberOption(0,12,"Speed",False,1,100,1,self.speed,self.setSpeed))
        self.displayOptions.addOption(selectOption(0,48,"Back",False,lambda: self.displayOptions.setMenuActive(False),self.backFunc))
    def enterMenu(self):
        self.displayOptions.setMenuActive(True)
    def getDisplayOptions(self):
        return self.displayOptions
    def update(self):
        super(servoSettings,self).update()
        self.displayOptions.update()
        # This also updates the globally config file somehow, so thats neat.
        self.config['start'] = self.displayOptions.menuItems[1].currentValue
        self.config['end'] = self.displayOptions.menuItems[2].currentValue
        self.config['pin'] = self.displayOptions.menuItems[3].currentValue
        self.config['invert'] = self.displayOptions.menuItems[4].currentValue
        self.config['speed'] = self.displayOptions.menuItems[6].currentValue


class neolightSettings(NeoLight):
    def __init__(self,config=None,backFunc=None):
        # Get config from pass config variable
        super().__init__(config)
        self.config = config
        self.backFunc = backFunc
        self.dop = Menu(False)
        self.dop.addOption(labelOption(0,0,"Light Settings"))
        self.dop.addOption(numberOption(0,12,"Pin",True,1,30,1,self.pin))
        self.dop.addOption(numberOption(0,24,"Length",False,1,30,1,self.length))
        self.dop.addOption(boolOption(0,36,"Flicker",False,self.flicker,self.setFlicker))
        self.dop.addOption(selectOption(0,48,"Back",False,lambda: self.dop.setMenuActive(False),self.backFunc))
    def enterMenu(self):
        self.dop.setMenuActive(True)
    def getdop(self):
        return self.dop
    def update(self):
        # super(neolightSettings,self).update()
        self.dop.update()
        # This also updates the globally config file somehow, so thats neat.
        self.config['pin'] = self.dop.menuItems[1].currentValue
        self.config['length'] = self.dop.menuItems[2].currentValue
        self.config['flicker'] = self.dop.menuItems[3].currentValue
# Holder for Options (above) it handles navigating up and down options and entering into another menu, also handles pagination sorta
class Menu:
    def __init__(self,active):
        self.menuItems = []
        self.menuActive = active
        self.y = 0
        self.increment = 12
        self.selected = 0
        # Number of items per "page"
        self.offset = 5
    def update(self):
        if self.menuActive:
            for i in range((math.ceil((max(1,self.selected + 1)) / self.offset) - 1) * self.offset, ((math.ceil((max(1,self.selected + 1)) / self.offset) - 1) * self.offset) + self.offset):
                if i < len(self.menuItems):
                    self.menuItems[i].updateDisplay()
                    self.menuItems[i].checkButtons()
                    self.menuItems[i].update()
            for i in range(len(self.menuItems)):
                if not self.menuItems[i].getEditing():
                    # Display little next / previous indicators
                    if len(self.menuItems) > 5:
                        if self.selected > 5:
                            display.text("<",0,0,1)
                        if self.selected < 5:
                            display.text(">",120,0,1)
                    if self.menuItems[i].getSelected():
                        self.selected = i
                        if cooldownBtn.getState():
                            for g in range(1,5):
                                if i + g < len(self.menuItems):
                                    #Remove button logic if label
                                    if self.menuItems[i + g].getName() != 'labelOption':
                                        self.menuItems[i + g].setSelected(True)
                                        self.menuItems[i].setSelected(False)
                                        break
                                else:
                                    # Allow cycling back to start of menu
                                    if self.menuItems[(0 + g) - 1].getName() != 'labelOption':
                                        self.menuItems[(0 + g) - 1].setSelected(True)
                                        self.menuItems[i].setSelected(False)
                                        break

                        if openCloseBtn.getState():
                            for g in range(1,5):
                                if i - g >= 0:
                                    #Remove button logic if label
                                    if self.menuItems[i - g].getName() != 'labelOption':
                                        self.menuItems[i - g].setSelected(True)
                                        self.menuItems[i].setSelected(False)
                                        break
                                if i - g < 0:
                                    # Allow cycling to end of menu
                                    if self.menuItems[len(self.menuItems) - g].getName() != 'labelOption':
                                        self.menuItems[len(self.menuItems) - g].setSelected(True)
                                        self.menuItems[i].setSelected(False)
                                        break

                        if fireBtn.getState():
                            self.menuItems[i].setEditing(True)
    def addOption(self,item):
        self.menuItems.append(item)
    def setMenuActive(self,menuActive):
        self.menuActive = menuActive


buffer, img_res = get_img()

fb = framebuf.FrameBuffer(buffer, img_res[0], img_res[1], framebuf.MONO_HMSB)

display.fill(0)
display.blit(fb, 0, 0)
display.show()

bness = 0
cooooldown = 0
cooldown = False
lock = False
count = 200



# Enable or disable settings menu
settings = False

# Current State
state = "open"

# Create progress bars
bars = []
# Create bars
# Amount (% from 0-100) | List of x and y or auto to automatically calculate height | Bar height in pixels | Min number | Max number
bars.append(ProgressBar(0,{'x':0,'y':'auto'},10,"heat"))
bars.append(ProgressBar(12,{'x':0,'y':'auto'},10,"ammo",min=0,max=12))


# Initialize all the buttons
openCloseBtn = Button(16,False)
cooldownBtn = Button(12,False)
fireBtn = Button(15,True)
reloadBtn = Button(14,True)
screenBtn = Button(13,True)

# If the down button is pressed while powering on, enter settings menu
if openCloseBtn.getState():
    settings = True
    

# Speed | pin | length | brightness | color
# toplight = NeoLight(1,config['lights']['topLight']['pin'],config['lights']['topLight']['length'],0,config['colors']['normal'])

# main logic loop
ammo = 4
heat = 0
heatIncBy = 25
fireTime = 100

# magLight = NeoLight(1,17,9,0,config['colors']['normal'],False)

# toplight.setBrightness(0)

vibrationMotor = Pin(config['vibrationMotor']['pin'],Pin.OUT)

barrelLed = Pin(config['lights']['barrelled']['pin'],Pin.OUT)

barrelLed.low()

#METHODS ==================================


count = 0
countover = 20
def updateDisplay(delta):
    global count,countover
    if count > delta:
        display.fill(0)
        for bar in bars:
            bar.update()
        display.show()
        count = 0
    else:
        count += 1

def debugDisplay(servos):
    global count,countover
    y = 0
    if count > countover:
        display.fill(0)
        for servo in servos:
            display.text(servo + " : " + str(servos[servo].isMoving()),0,y,1)
            y += 12
        display.show()
        count = 0
    else:
        count += 1

def changeState(toChange):
    global state
    state = toChange

def settingsLoop():
    global settings
    if settings:
        display.fill(0)
        main_menu.update()
        servoMenu.update()
        lightMenu.update()
        miscMenu.update()
        motor_menu.update()
        barrel_led_menu.update()
        for servo in servos:
            servos[servo].update()
        for light in lights:
            lights[light].update()
        display.show()
        return True
    else:
        return False
# Exit settings menu and save the config file
def exitMenu():
    global settings
    file = open("config","wb")
    file.write(json.dumps(config))
    file.close()
    settings = False
    reset()


# Build servo settings menu from config file
servos = {}
lights = {}

def savemotormenu(value):
    config['vibrationMotor']['pin'] = value
def savebarrelled(value):
    config['barrelled']['pin'] = value

if settings:
    main_menu = Menu(True)
    main_menu.addOption(labelOption(0,0,"Main Menu"))
    servoMenu = Menu(False)
    lightMenu = Menu(False)
    barrel_led_menu = Menu(False)
    motor_menu = Menu(False)
    miscMenu = Menu(False)

    main_menu.addOption(selectOption(0,12,"Servo Settings",True,lambda: servoMenu.setMenuActive(True),lambda: main_menu.setMenuActive(False)))
    main_menu.addOption(selectOption(0,24,"Light Settings",False,lambda: lightMenu.setMenuActive(True),lambda: main_menu.setMenuActive(False)))
    main_menu.addOption(selectOption(0,36,"Misc Settings",False,lambda: miscMenu.setMenuActive(True),lambda: main_menu.setMenuActive(False)))
    main_menu.addOption(selectOption(0,48,"Save And Exit",False,exitMenu))
    # Servo menu options
    y = 12
    inc = 12
    once = True
    servoMenu.addOption(labelOption(0,0,"Servo Settings"))
    for servoOptions in config['servos']:
        servo = servoSettings(config['servos'][servoOptions],lambda: servoMenu.setMenuActive(True))
        servoMenu.addOption(selectOption(0,y,servoOptions,once,servo.enterMenu,lambda: servoMenu.setMenuActive(False)))
        servos[servoOptions] = servo
        y += inc
        if y > 48:
            servoMenu.addOption(labelOption(0,0,"Servo Settings"))
            y = 12
        once = False
    servoMenu.addOption(selectOption(0,48,"< Back",False,lambda: servoMenu.setMenuActive(False),lambda: main_menu.setMenuActive(True)))

    # Light Menu Options
    y = 12
    inc = 12
    once = True
    lightMenu.addOption(labelOption(0,0,"Light Settings"))
    
    for lightOption in config['lights']:
        if lightOption != "barrelled":
            light = neolightSettings(config['lights'][lightOption],lambda: lightMenu.setMenuActive(True))
            lightMenu.addOption(selectOption(0,y,lightOption,once,light.enterMenu,lambda: lightMenu.setMenuActive(False)))
            lights[lightOption] = light
            y += inc
            if y > 48:
                lightMenu.addOption(labelOption(0,0,"Light Settings"))
                y = 12
            once = False
    lightMenu.addOption(selectOption(0,48,"< Back",False,lambda: lightMenu.setMenuActive(False),lambda: main_menu.setMenuActive(True)))

    miscMenu.addOption(labelOption(0,0,"Misc Settings"))
    miscMenu.addOption(selectOption(0,12,"Motor",True,lambda: motor_menu.setMenuActive(True),lambda: miscMenu.setMenuActive(False)))
    miscMenu.addOption(selectOption(0,24,"Barrel LED",False,lambda: barrel_led_menu.setMenuActive(True),lambda: miscMenu.setMenuActive(False)))
    miscMenu.addOption(selectOption(0,48,"< Back",False,lambda: miscMenu.setMenuActive(False),lambda: main_menu.setMenuActive(True)))


    # Motor menu
    motor_menu.addOption(labelOption(0,0,"Motor"))
    motor_menu.addOption(numberOption(0,12,"Pin",True,1,30,1,config['vibrationMotor']['pin'],savemotormenu))

    motor_menu.addOption(selectOption(0,48,"< Back",False,lambda: motor_menu.setMenuActive(False),lambda: miscMenu.setMenuActive(True)))

    # Led menu
    barrel_led_menu.addOption(labelOption(0,0,"Barrel LED"))
    barrel_led_menu.addOption(numberOption(0,12,"Pin",True,1,30,1,config['lights']['barrelled']['pin'],savebarrelled))
    barrel_led_menu.addOption(selectOption(0,48,"< Back",False,lambda: barrel_led_menu.setMenuActive(False),lambda: miscMenu.setMenuActive(True)))

else:
    for servo in config['servos']:
        servos[servo] = Servo(config['servos'][servo])
    for light in config['lights']:
        if light != "barrelled":
            lights[light] = NeoLight(config['lights'][light])
    

# Update servos once before continuing (sets them to the same position as in the config file)
for servo in servos:
    servos[servo].update()



class State():
    def __init__(self):
        pass
    # Things to happen when entering this state (only happens once)
    def enter(self,sm):
        pass
    # Things to happen every update loop
    def update(self,sm):
        pass
    # Things to happenwhen exiting state
    def exit(self,sm):
        pass

# ========= States ===============
class Main(State):
    def __init__(self):
        super().__init__()
        # 20 cycles for one shot (Maybe load in via config)
        servos['barrelEnd'].setSpeed(100)
        servos['barrelEnd'].setPos(35)
    def update(self,sm):
        # Main Loop
        if sm.ammo == 0 or cooldownBtn.getState(False):
            sm.changeState(Cooldown())
        if fireBtn.getState(False) and sm.heat < 100:
            sm.changeState(FireBuildup())
        if openCloseBtn.getState():
            sm.changeState(Closing())
        if sm.heat >= 0:
            sm.heat = sm.heat - 0.005
        if screenBtn.getState():
            servos['screen'].toggle()

class FireBuildup(State):
    def __init__(self):
        super().__init__()
        self.triggerPullCounter = Timer(0,20,0.2)
    def enter(self, sm):
        servos['barrelEnd'].setSpeed(100)
    def update(self, sm):
        fireBtn.getState()
        if not fireBtn.getHeld():
            sm.changeState(Main())
        sm.heat = sm.heat + 0.2
        if self.triggerPullCounter.update(True):
            sm.changeState(Firing())
        servos['barrelEnd'].setPos((self.triggerPullCounter.current * 2) + 35)

class Opening(State):
    def __init__(self):
        super().__init__()
        self.timer = Timer(0,100,1)
    def update(self,sm):
        servos['top1'].open()
        servos['top2'].open()
        servos['top3'].open()
        if not servos['top1'].isMoving() and not servos['top2'].isMoving() and not servos['top3'].isMoving():
            servos['barrelEnd'].setPos(35)
            if self.timer.update(True):
                if not servos['barrelEnd'].isMoving():
                    servos['barrel'].open()
                    if not servos['barrel'].isMoving():
                        sm.changeState(Main())

class Closing(State):
    def __init__(self):
        super().__init__()
        self.timer = Timer(0,100,1)
    def update(self, sm):
        servos['barrel'].close()
        if self.timer.update(True):
            if not servos['barrel'].isMoving():
                servos['barrelEnd'].close()
                if not servos['barrelEnd'].isMoving():
                    servos['top1'].close()
                    servos['top2'].close()
                    servos['top3'].close()
                    if not servos['top1'].isMoving() and not servos['top2'].isMoving() and not servos['top3'].isMoving():
                        sm.changeState(Closed())

class Closed(State):

    def __init__(self):
        super().__init__()
    def update(self, sm):
        if openCloseBtn.getState():
            sm.changeState(Opening())

class Cooldown(State):
    def __init__(self):
        global heat
        super().__init__()
        self.cooldownSpeed = 0.1
    def enter(self,sm):
        self.animateToBlueTimer = Timer(0,sm.heat / 2,self.cooldownSpeed)
        self.animateToOffTimer = Timer(0,sm.heat / 2,self.cooldownSpeed)
    def update(self, sm):
        lights['toplight'].animateColor(config['colors']['cooldown'],self.cooldownSpeed)
        sm.heat = sm.heat - self.cooldownSpeed
        if self.animateToBlueTimer.update(True):
            if self.animateToOffTimer.update(True):
                lights['toplight'].setColor(config['colors']['normal'])
                if sm.ammo == 0:
                    sm.changeState(Reload())
                else:
                    sm.changeState(Main())
                sm.heat = 0
        lights['toplight'].setBrightness(int(sm.heat))

class Firing(State):
    def __init__(self):
        super().__init__()
        self.returnBarrelTimer = Timer(0,50,1)
        self.blink = Timer(0,50,1)
    def enter(self, sm):
        sm.ammo -= 1
        barrelLed.high()
        servos['barrelEnd'].setSpeed(200)
        servos['barrelEnd'].setPos(35)
    def update(self, sm):
        if self.blink.update(True):
            barrelLed.low()
        vibrationMotor.high()
        lights['toplight'].setColor([[225, 205, 205], [0, 0, 0]])
        servos['barrel'].setSpeed(200)
        servos['barrel'].close()
        if self.returnBarrelTimer.update(True):
            vibrationMotor.low()
            lights['toplight'].setColor(config['colors']['normal'])
            servos['barrel'].setSpeed(50)
            servos['barrel'].open()
            sm.changeState(AfterShot())

class AfterShot(State):
    def __init__(self):
        super().__init__()
    def enter(self, sm):
        if ammo == 0:
            sm.changeState(Cooldown())
    def update(self, sm):
        fireBtn.getState(False)
        if not fireBtn.getHeld():
            sm.changeState(Main())

class Reload(State):
    def __init__(self):
        super().__init__()
    def update(self, sm):
        lights['maglight'].setColor(config['colors']['normal'])
        lights['maglight'].setBrightness(100)
        lights['maglight'].update()
        if reloadBtn.getState(False):
            sm.changeState(Reloaded())

class Reloaded(State):
    def __init__(self):
        super().__init__()
        self.pulseCounter = 0
        self.sign = -1
    def update(self, sm):
        global ammo
        lights['maglight'].setColor(config['colors']['reloading'])
        if lights['maglight'].brightness >= 100:
            self.sign = -1
        elif lights['maglight'].brightness <= 0:
            self.sign = 1
            self.pulseCounter += 1
        lights['maglight'].setBrightness(lights['maglight'].brightness + self.sign)
        if self.pulseCounter > 3:
            sm.ammo = sm.maxAmmo
            lights['maglight'].setBrightness(0)
            lights['maglight'].update()
            sm.changeState(Main())
        lights['maglight'].update()
# Handles states
class StateMachine():
    def __init__(self,starting):
        self.currentState = starting
        # Settings
        self.heat = 0
        self.maxAmmo = 12
        self.ammo = self.maxAmmo

    def changeState(self,state):
        if self.changeState:
            self.currentState.exit(self)

        self.currentState = state

        if self.currentState:
            self.currentState.enter(self)
        config['state'] = type(state).__name__
        saveSettings()

    def getCurrentState(self):
        return self.currentState

    def update(self):
        self.currentState.update(self)
        for servo in servos:
            if servos[servo].isMoving():
                servos[servo].update()
        updateDisplay(2)
        lights['toplight'].setBrightness(self.heat)
        lights['toplight'].update()


# Load into previously saved state:
# Only if one of the "safe" states
if config['state'] == 'Main' or config['state'] == 'Closed':
    state = config['state']
else:
    state = 'Closed'

constructor = globals()[state]

mainLogic = StateMachine(constructor())


# MAIN LOOP
loopstart = utime.time()


while True:
    loopstart = utime.ticks_cpu()
    # Handling settings loop
    if settingsLoop():
        continue
    # debugDisplay(servos)
    # Main loop
    bars[1].setAmount(mainLogic.ammo)
    bars[0].setAmount(mainLogic.heat)
    mainLogic.update()

    delta = utime.ticks_cpu() - loopstart