import cv2
import numpy as np
import pyautogui
import keyboard
import time
import win32api
from win32con import *
import ctypes
import winreg
from tkinter import *
import os
import json
import sys

os.system("color")
GRAY = "\033[90m"
PINK = "\033[95m"
CYAN = "\033[36m"
RESET = "\033[0m"
        
class Display:
        
    def logo():
        print("{}Ü Wäñ± ßä][øøñ$\n{}1930s Hardware\n{}SCOPE v1.0\n{}2023{}\n".format(PINK, GRAY, RESET, GRAY, RESET))
    
    def positionalInstructions():
        print("{}Right-click on the window header.".format(GRAY))
        print("Select move, then align the crosshairs.")
        print("Now click on the Set Location button.\n{}".format(RESET))
    
    def instructions():
        print("Scope ready...")
        print("{}<{}Shift{}> up/down".format(GRAY, CYAN, GRAY))
        print("<{}Q{}> to quit{}".format(CYAN, GRAY, RESET))
    
class SetWindow:
    
    def __init__(self, x, y):
        self.win = Tk()
        self.x = x
        self.y = y
        self.coords = []
    
    def get_window_location(self):
        # Get the window location and close window
        window_location = self.win.geometry()
        location = window_location.split("+")
        x = int(location[1])
        y = int(location[2]) + 40
        self.coords = [x, y]
        self.win.destroy()
    
    def now(self):
        Display.positionalInstructions()
        pos = "+{}+{}".format(self.x, self.y)
        # Set the window size
        self.win.geometry("80x80"+pos)
        # Set the window attributes to make it see-through
        self.win.attributes("-alpha", 0.5)
        # Set canvas crosshairs
        canvas = Canvas(self.win, width=80, height=80)
        canvas.pack()
        canvas.place(x=0, y=0, width=80, height=80)
        line = canvas.create_line(40, 0, 40, 80, fill="red", width=1)
        line2 = canvas.create_line(0, 40, 80, 40, fill="red", width=1)
        # Create a button to get the window location
        get_location_button = Button(self.win, text="Set Location", command=self.get_window_location)
        get_location_button.pack()
        self.win.mainloop()
        X = self.coords[0] + 7
        Y = self.coords[1] - 9
        return X, Y

class QuickScope:
    
    def __init__(self, reset=False, scope_location=[]):
        os.system("cls")
        Display.logo()
        if not os.path.exists("coords.json") or reset:
            # set the capture area
            print("Setup..")
            screen_width, screen_height = pyautogui.size()
            halfX = int(screen_width / 2)
            halfY = int(screen_height / 2)
            getTheCentre = SetWindow(halfX, halfY)
            X, Y = getTheCentre.now()
            self.modX = X
            self.modY = Y
            # save coords
            with open("coords.json", "w") as f:
                data = {"x": X, "y": Y}
                json.dump(data, f)
        else:
            # load coords
            with open("coords.json") as f:
                data = json.load(f)
                self.modX = data["x"]
                self.modY = data["y"]
        # set scope location
        if scope_location:
            self.scopeLocationX = scope_location[0]
            self.scopeLocationY = scope_location[1]
        else:
            self.scopeLocationX = 610
            self.scopeLocationY = 635
        # scope dimensions
        self.width = 400
        self.height = 400
        self.dim = (self.width, self.height)
        # scope image
        scope_img = cv2.imread("scope.png")
        self.scope_img = cv2.resize(scope_img, self.dim, interpolation=cv2.INTER_AREA)
        self.operating = False
        self.looping = True
        self.cms = 0
        self.hms = 0

    def get_mouse_sensitivity(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse")
            value, _ = winreg.QueryValueEx(key, "MouseSensitivity")
            winreg.CloseKey(key)
            value = int(value)
        except FileNotFoundError:
            value = 20
        return value
 
    def mouseWheel(self, direction, amount=1):
        if direction == "down":
            amount = -(amount)
        (x, y) = pyautogui.position()
        win32api.mouse_event(MOUSEEVENTF_WHEEL, x, y, amount, 0)
    
    def mouseSpeed(self, speed=10):
        set_mouse_speed = 113
        ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, speed, 0)
    
    def setModifier(self):
        (posX, posY) = pyautogui.position()
        self.accuracy_modifierX = posX - self.modX
        self.accuracy_modifierY = posY - self.modY
 
    def checkKeyboard(self):
        if keyboard.is_pressed("shift"):
            if self.operating:
                self.operating = False
                print("idle...   ", end="\r")
                cv2.destroyAllWindows()
                self.mouseSpeed(speed=self.cms)
                for z in range(0, 4):
                    self.mouseWheel("down", amount=2)
                    time.sleep(0.3)
            else:
                self.operating = True
                print("active... ", end="\r")
                self.setModifier()
                self.scopeUp()
                self.mouseSpeed(self.hms)
                self.mouseWheel("up", amount=4)
            time.sleep(0.2)
        elif keyboard.is_pressed("q"):
            cv2.destroyAllWindows()
            self.operating = False
            self.looping = False
            print("goodbye...")
    
    def scopeUp(self):
        # Create a named window, Set the window to be always on top and borderless, then resize and move location
        cv2.namedWindow("scope", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("scope", cv2.WND_PROP_TOPMOST, 1)
        cv2.setWindowProperty("scope", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  
        cv2.resizeWindow("scope", self.width, self.height)
        cv2.moveWindow("scope", self.scopeLocationX, self.scopeLocationY)
    
    def now(self):
        Display.instructions()
        # get current mouse sensitivity
        self.cms = self.get_mouse_sensitivity()
        # define half mouse sensitivity
        self.hms = int(self.cms / 2)
        
        while self.looping:
            self.checkKeyboard()
            if self.operating:
                # get centre screenshot in relation to mouse
                (posX, posY) = pyautogui.position()
                absolute_X = posX - self.accuracy_modifierX
                absolute_Y = posY - self.accuracy_modifierY
                img = pyautogui.screenshot(region=(absolute_X, absolute_Y, 80, 80))
                img = np.array(img)
                # scale the image up
                img = cv2.resize(img, self.dim, interpolation = cv2.INTER_AREA)
                # convert the image to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Blend the images
                blended_image = cv2.addWeighted(img, 0.5, self.scope_img, 1, 0)
                cv2.imshow("scope", blended_image)
                if cv2.waitKey(1) == ord("q"):
                    break
                    cv2.destroyAllWindows() 


if len(sys.argv) > 1:
    if sys.argv[1].lower() == "-reset":
        reset = True
else:
    reset = False
    
gimmeTheScope = QuickScope(reset=reset)
gimmeTheScope.now()
