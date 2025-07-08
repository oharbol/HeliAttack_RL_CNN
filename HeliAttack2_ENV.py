import gymnasium as gym
import numpy as np
from gymnasium import spaces

# Not used but needed for some stupid reason for pynput to work
import pyautogui
from PIL import ImageGrab
import time
import pynput
from pynput.mouse import Button
from pynput.keyboard import Key


# Timing improvements
# Each step (pyautogui):
# Was 0.65 sec
# Now 0.26 sec      Improvement = -0.39 sec
# Each step (pynput):
# Was 0.65 sec
# Now 0.025 sec      Improvement = -0.625 sec

# Reset Variables:
# Was 0.55 sec
# Now 0.10 sec      Improvement = 0.45 sec

# All other processes take 0.02 seconds
# Image grab 0.05 seconds

# Constant variables
SCREEN_X = 198
SCREEN_Y = 328
SCORE_X_POS = 58
SCORE_Y_POS = 23
WIDTH = 563
HEIGHT = 378
SCORE_HEIGHT = 9
SCORE_ALT_WIDTH = 4

LEFT_LIMIT = 150
RIGHT_LIMIT = 810
MOUSE = 55

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

        # Pixel Variables
        self.health_y_list = [6,11,21,30,40,50,60,70,79,89]
        self.pixel_4 = [[4,1], [5,1], [6,1], [6,2], [6,3], [6,4], [1,5], [6,5], [6,6], [6,7], [6,8]]
        self.pixel_5 = [[1,1], [1,2], [1,3], [1,4], [7,6]]
        self.pixel_6 = [[1,2], [1,3], [1,4], [1,5], [1,6], [7,6]]


        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(7)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(HEIGHT * 3, WIDTH), dtype=np.uint8) # shape=(HEIGHT, WIDTH, 3)
        
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

        # Get overall screen
        #pix = self.grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)
        im = ImageGrab.grab([SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT])
        pix = im.load()


        # Get new game score
        last_score = self.score
        self.score = self.get_score(pix)

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
        self.health = self.get_health(self.health, pix)

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
        self.steps += 1
        # if(self.steps % 1000 == 0):
        #     print("Step: ", self.steps)

        # Save new images
        self.image_3 = self.image_2
        self.image_2 = self.image_1
        self.image_1 = im.convert("L")
        
        #np.concatenate((self.image_1, self.image_2, self.image_3))
        #np.asarray(self.image_1)
        return np.concatenate((self.image_1, self.image_2, self.image_3)) , reward, done, self.truncated, info


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
            #pyautogui.moveTo(400, 620, duration=0.5)
            mouse.position = (400, 620)
            time.sleep(0.5)
            #pyautogui.click(clicks=2)
            mouse.press(Button.left)
            mouse.release(Button.left)

            # Click "Start Button"
            #pyautogui.moveTo(662, 697, duration=0.5)
            mouse.position = (662, 697)
            time.sleep(0.5)
            #pyautogui.click(clicks=2)
            mouse.press(Button.left)
            mouse.release(Button.left)

            # Move Mouse to Starting Position
            #pyautogui.moveTo(480, 328)
            mouse.position = (480, 315)

            # Wait for paratrooper to land
            time.sleep(3)
        
        # Get overall screen
        #pix = self.grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)
        im = ImageGrab.grab([SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT])

        # Save initial images
        self.image_1 = im.convert("L")
        self.image_2 = im.convert("L")
        self.image_3 = im.convert("L")
       
        # np.concatenate((self.image_1, self.image_2, self.image_3))
        #np.asarray(self.image_1)
        return np.concatenate((self.image_1, self.image_2, self.image_3)), info


    # Close File
    def close(self):
        print("Testing Over!")


    # Helper Functions
    # Takes screen shot of designated area
    # Automatically does not save screen shot
    # def grab_screenshot(self, x,y,x2,y2):
    #     im = ImageGrab.grab([x, y, x2, y2])
    #     pix = im.load()

    #     return pix, im
    
    # Function to find changes to health
    def get_health(self, curr_health, pix):
        #Get colored pixel of health at last red level
        color = pix[552, self.health_y_list[10 - curr_health]]

        #Player was hit
        #If white/gray pixel is observed reduce heath
        if(color[0] == color[1]):
            curr_health -= 1

        #Check if med pack was picked up
        if(curr_health == 9):
            #Get colored pixel at space 10
            color = pix[552, self.health_y_list[0]]
            if(color[0] > color[1] and color[1] != color[2]):
                curr_health += 1
        elif(curr_health < 9):
            #Get colored pixel at space above 2 health levels
            color = pix[552, self.health_y_list[8 - curr_health]]
            if(color[0] > color[1] and color[1] != color[2]):
                curr_health += 2
        
        return curr_health

    #Translate Score Letter Pixels to list of white pixels in image
    #Temporary list to hold white pixel locations
    def find_white_pixels(self, start_x, start_y, x_pix, y_pix, pixels):
        #Return list
        white_px = []

        #Loop through all pixels
        for y in range(start_y, start_y + y_pix):
            for x in range(start_x, start_x + x_pix):
                #Get pixel color
                temp = pixels[x,y]
                #Check for white pixels
                if(temp[0] == 255 and temp[1] == 255 and temp[2] == 255):
                    white_px.append([x - (SCORE_X_POS + self.score_x), y - SCORE_Y_POS])

        return white_px
    
    #Switch Case to get number from white pixels
    def get_score_num(self, list_pix):
        match len(list_pix):
            case 3:
                return 3
            case 4:
                return 2
            case 5:
                for x in list_pix:
                    if(x not in self.pixel_5):
                        return 7
                return 5
            case 6:
                for x in list_pix:
                    if(x not in self.pixel_6):
                        return 8
                return 6
            case 7:
                return 9
            # case 8:
            #     return 1
            case 10:
                return 0
            case 11:
                for x in list_pix:
                    if(x not in self.pixel_4):
                        return 0
                return 4
            case _:
                return -1
    
    # Function to get current score
    def get_score(self, pix):
        curr_score = 0
        score_temp = 0

        # Loop until 
        while score_temp != -1:
            # multiply score by 10 and add temp score
            if(score_temp == 0):
                curr_score = curr_score * 10
            else:
                curr_score = (curr_score * 10) + score_temp

            #Check first 4 pixels if image is one
            white_px = self.find_white_pixels(SCORE_X_POS + self.score_x, SCORE_Y_POS, SCORE_ALT_WIDTH, SCORE_HEIGHT, pix)

            #Post process pixels to determine if "1"
            if(len(white_px) == 8):
                score_temp = 1
                self.score_x += SCORE_ALT_WIDTH + 1
            else:

                #Otherwise check first 9 pixels if value is "2"-"9"
                white_px = self.find_white_pixels(SCORE_X_POS + self.score_x, SCORE_Y_POS, SCORE_HEIGHT, SCORE_HEIGHT, pix)

                #Post process pixels to compare what value
                score_temp = self.get_score_num(white_px)

                self.score_x += SCORE_HEIGHT + 1
        
        return curr_score