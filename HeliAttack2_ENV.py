import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.spaces import Dict, Box, Discrete, Text
from gymnasium.wrappers import FlattenObservation

# Not used but needed for some stupid reason for pynput to work
import pyautogui
from PIL import ImageGrab
import time
import pynput
from pynput.mouse import Button
from pynput.keyboard import Key
import string

# Constant variables
SCREEN_X = 254 #198
SCREEN_Y = 370 #328
WIDTH = 452
HEIGHT = 322

# Score Screen Constants
SCORE_X = 47 + SCREEN_X
SCORE_Y = 19 + SCREEN_Y
SCORE_WIDTH = 80
SCORE_HEIGHT = 8

# Health Screen Constants
HEALTH_X = 434 + SCREEN_X
HEALTH_Y = 4 + SCREEN_Y
HEALTH_WIDTH = 13
HEALTH_HEIGHT = 72

LEFT_LIMIT = 150
RIGHT_LIMIT = 810
MOUSE = 55

WHITE_PIX = (255, 255, 255)
WHITE_RED_PIX = (255, 254, 254)

# Input handler variables
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()


# Environment Class
class HeliAttackEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    def __init__(self):
        super().__init__()
        self.truncated = False

        # Self Fields
        # Manipulated variables
        self.last_score = 0
        self.score = 0
        self.last_health = 0
        self.health = 0

        self.score_x = 0

        self.steps = 0

        self.action_last = 0

        # Value between 0-12
        # Left limit 0
        # Right limit 12
        # Middle at 6
        self.position = 6

        # Images to save
        self.image_1 = []
        self.image_2 = []
        self.image_3 = []


        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(7)
        # Example for using image as input (channel-first; channel-last also works):
        # self.observation_space = spaces.Box(low=0, high=255,
        #                                     shape=(HEIGHT * 3, WIDTH), dtype=np.uint8) # shape=(HEIGHT, WIDTH, 3)
        
        # Multi Policy Observation Space
        self.observation_space = Dict({
            "health": Discrete(11),
            "score": Discrete(2147483), # Text(1),
            "images": Box(low=0, high=255, shape=(HEIGHT, WIDTH), dtype= np.uint8)
        })

        

    # ACTIONS
    # 0 - Left
    # 1 - Right
    # 2 - Jump
    # 3 - Duck
    # 4 - Mouse Left
    # 5 - Mouse Right
    # 6 - Shoot
    # 7 - Do nothing
    def step(self, action):
        info = {}
        reward = 0
        done = False

        # Reset inputs
        if(self.action_last == 0):
            #pyautogui.keyUp('left')
            keyboard.release(Key.left)
        elif(self.action_last == 1):
            #pyautogui.keyUp('right')
            keyboard.release(Key.right)
        elif(self.action_last == 2):
            #pyautogui.keyUp('up')
            keyboard.release(Key.up)
        elif(self.action_last == 3):
            #pyautogui.keyUp('down')
            keyboard.release(Key.down)
        else:
            #pyautogui.mouseUp()
            mouse.release(Button.left)

        # Move Left
        if(action == 0):
            #pyautogui.keyDown('left')
            keyboard.press(Key.left)
            self.action_last = 0
        
        # Move Right
        elif(action == 1):
            #pyautogui.keyDown('right')
            keyboard.press(Key.right)
            self.action_last = 1

        # Jump
        elif(action == 2):
            #pyautogui.keyDown('up')
            keyboard.press(Key.up)
            self.action_last = 2

        # Duck
        elif(action == 3):
            #pyautogui.keyDown('down')
            keyboard.press(Key.down)
            self.action_last = 3

        # Move mouse left
        elif(action == 4 and self.position > 0):
            #pyautogui.move(-MOUSE, 0)
            mouse.move(-MOUSE, 0)
            self.position -= 1
            self.action_last = 4
        
        # Move mouse right
        elif(action == 5 and self.position < 12):
            #pyautogui.move(MOUSE, 0)
            mouse.move(MOUSE, 0)
            self.position += 1
            self.action_last = 5

        # Shoot
        elif(action == 6):
            #pyautogui.mouseDown()
            mouse.press(Button.left)
            self.action_last = 6
        
        # Do nothing (action == 7)

        # Get new game score
        last_score = self.score
        self.score = self.get_score()

        # Reset score x variable
        self.score_x = 0

        # Increase reward each hit
        if(last_score < self.score):
            reward += 5

        # Larger reward for downing helicopter
        if(self.score // 30000 > last_score // 30000):
            reward += 300
            done = True


        # Check health
        last_health = self.health
        self.health = self.get_health()

        # Reduce reward if hit
        if(last_health > self.health):
            reward -= 100

        # End game if dead
        if(self.health <= 0):
            done = True
            # reward -= 500
            # reward += -300 + (self.steps / 15) #600 seconds goal decreased by time survived

        # Reward for living
        else:
            reward -= 0.5
        
        # DEBUGGING CODE
        # self.steps += 1
        # if(self.steps % 1000 == 0):
        #     print("Step: ", self.steps)

        # Reward 3
        # Reward (positive) is a fraction based on the current health
        # if(reward > 0):
        #     reward *= round(1 / self.health, 1) 

        # Reward 4
        # Reward based on difference between last health and time between heli kills

        # Get overall screen
        #pix = self.grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)
        im = ImageGrab.grab([SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT])
        
        # Save new images
        # self.image_3 = self.image_2
        # self.image_2 = self.image_1
        self.image_1 = im.convert("L")
        
        #np.concatenate((self.image_1, self.image_2, self.image_3))
        #np.asarray(self.image_1)

        # Multi Policy Observation Space
        observation = {
            "health": self.health,
            "score": self.score // 1000,
            "images": np.asarray(self.image_1)
        }

        return observation, reward, done, self.truncated, info


    def reset(self, seed=None, options=None):
        info = {}

        # Check if died
        if(self.health <= 0):
            self.last_score = 0
            self.score = 0
            self.last_health = 0
            self.health = 10
            self.position = 6
            self.steps = 1

            self.score_x = 0

            # Reset inputs
            if(self.action_last == 0):
                #pyautogui.keyUp('left')
                keyboard.release(Key.left)
            elif(self.action_last == 1):
                #pyautogui.keyUp('right')
                keyboard.release(Key.right)
            elif(self.action_last == 2):
                #pyautogui.keyUp('up')
                keyboard.release(Key.up)
            elif(self.action_last == 3):
                #pyautogui.keyUp('down')
                keyboard.release(Key.down)
            else:
                #pyautogui.mouseUp()
                mouse.release(Button.left)

            # Wait for death screen
            time.sleep(7.5)

            # Click to open main menu
            mouse.position = (SCREEN_X + 158, SCREEN_Y + 234) #400, 620
            time.sleep(0.5)
            mouse.press(Button.left)
            mouse.release(Button.left)

            # Click "Start Button"
            mouse.position = (SCREEN_X + 372, SCREEN_Y + 296) #662, 697
            time.sleep(0.5)
            mouse.press(Button.left)
            mouse.release(Button.left)

            # Move Mouse to Starting Position
            mouse.position = (SCREEN_X + 226, 315) #480, 315

            # Wait for paratrooper to land
            time.sleep(3)
        
        # Get overall screen
        #pix = self.grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)
        im = ImageGrab.grab([SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT])

        # Save initial images
        self.image_1 = im.convert("L")
        # self.image_2 = im.convert("L")
        # self.image_3 = im.convert("L")
       
        # np.concatenate((self.image_1, self.image_2, self.image_3))
        #np.asarray(self.image_1)

        # Multi Policy Observation Space
        observation = {
            "health": self.health,
            "score": self.score // 1000,
            "images": np.asarray(self.image_1)
        }

        return observation, info


    # Close File
    def close(self):
        print("Testing Over!")


    # Helper Functions
    
    def get_health(self):
        im = ImageGrab.grab([HEALTH_X, HEALTH_Y, HEALTH_X + HEALTH_WIDTH, HEALTH_Y + HEALTH_HEIGHT])
        pix = im.load()

        temp = self.health
        if(temp == 1):
            y = 67
        else:
            y = 2 + (10 - temp) * 8
        x = 3

        #Player hit
        if(pix[x,y] == WHITE_PIX or pix[x,y] == WHITE_RED_PIX):
            temp -= 1

        #Medpack picked up
        elif(temp == 9 and pix[x,y-8] != WHITE_PIX and pix[x,y-8] != WHITE_RED_PIX):
            temp += 1

        #Health less than 9
        elif(temp < 9 and pix[x,y-16] != WHITE_PIX and pix[x,y-16] != WHITE_RED_PIX):
            temp += 2

        return temp
        
        
    # Method to determine current score
    def get_score(self):

        im = ImageGrab.grab([SCORE_X, SCORE_Y, SCORE_X + SCORE_WIDTH, SCORE_Y + SCORE_HEIGHT])
        pix = im.load()

        # Establish variables
        x = 0
        curr_score = 0
        temp = 0

        while temp != -1:
            # Update score
            curr_score = (curr_score * 10) + temp
            # Reset list to empty list
            white_pixels = []

            # Loop through all pixels in 3x8 image of each number
            for i in range(0,8):
                # If white pixel in first row, add y variable to list
                if(pix[x,i] == WHITE_PIX): 
                    white_pixels.append(i)

            # Use switch case to determine which number is used
            match white_pixels:
                # Number is 0 or 6
                case [1,2,3,4,5]:
                    if(pix[x+2, 3] == WHITE_PIX):
                        temp = 6
                    else:
                        temp = 0
                # Number is 1
                case [1]:
                    temp = 1
                # Number is 2
                case [1,5,6]:
                    temp = 2
                # Number is 3
                case [1,5]:
                    temp = 3
                # Number is 4
                case [3,4]:
                    temp = 4
                # Number is 5
                case [0,1,2,3,5]:
                    temp = 5
                # Number is 7
                case [0]:
                    temp = 7
                # Number is 8
                case [1,2,4,5]:
                    temp = 8
                # Number is 9
                case [1,2,5]:
                    temp = 9
                # End of score reached
                case _:
                    temp = -1
            
            if(temp == 1):
                x += 4
            else:
                x += 8

        return curr_score