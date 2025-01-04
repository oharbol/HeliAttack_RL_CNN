import gymnasium as gym
import numpy as np
from gymnasium import spaces

import pyautogui
from PIL import ImageGrab
import time

#TODO Finish reset function
#TODO Move helpter functions to inside environment class
#TODO Move all manipulated variables to constructor and add ".self"

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

# Manipulated variables
last_score = 0
score = 0
last_health = 0
health = 10

score_x = 0

# Pixel Variables
health_y_list = [6,11,21,30,40,50,60,70,79,89]
pixel_4 = [[4,1], [5,1], [6,1], [6,2], [6,3], [6,4], [1,5], [6,5], [6,6], [6,7], [6,8]]
pixel_5 = [[1,1], [1,2], [1,3], [1,4], [7,6]]
pixel_6 = [[1,2], [1,3], [1,4], [1,5], [1,6], [7,6]]


# Helper Functions

# Takes screen shot of designated area
# Automatically does not save screen shot
def grab_screenshot(x,y,x2,y2):
    im = ImageGrab.grab([x, y, x2, y2])
    pix = im.load()

    return pix

# Function to find changes to health
def get_health(curr_health, pix):
    #Get colored pixel of health at last red level
    color = pix[552, health_y_list[10 - curr_health]]

    #Player was hit
    #If white/gray pixel is observed reduce heath
    if(color[0] == color[1]):
        curr_health -= 1

    #Check if med pack was picked up
    if(curr_health == 9):
        #Get colored pixel at space 10
        color = pix[552, health_y_list[0]]
        if(color[0] > color[1] and color[1] != color[2]):
            curr_health += 1
    elif(curr_health < 9):
        #Get colored pixel at space above 2 health levels
        color = pix[552, health_y_list[8 - curr_health]]
        if(color[0] > color[1] and color[1] != color[2]):
            curr_health += 2
    
    return curr_health

#Translate Score Letter Pixels to list of white pixels in image
#Temporary list to hold white pixel locations
def find_white_pixels(start_x, start_y, x_pix, y_pix, pixels):
    #Return list
    white_px = []

    #Loop through all pixels
    for y in range(start_y, start_y + y_pix):
        for x in range(start_x, start_x + x_pix):
            #Get pixel color
            temp = pixels[x,y]
            #Check for white pixels
            if(temp[0] == 255 and temp[1] == 255 and temp[2] == 255):
                white_px.append([x - (SCORE_X_POS + score_x), y - SCORE_Y_POS])

    return white_px

#Switch Case to get number from white pixels
def get_score_num(list_pix):
    match len(list_pix):
        case 3:
            return 3
        case 4:
            return 2
        case 5:
            for x in list_pix:
                if(x not in pixel_5):
                    return 7
            return 5
        case 6:
            for x in list_pix:
                if(x not in pixel_6):
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
                if(x not in pixel_4):
                    return 0
            return 4
        case _:
            return -1

# Function to get current score
def get_score(pix):
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
        white_px = find_white_pixels(SCORE_X_POS + score_x, SCORE_Y_POS, SCORE_ALT_WIDTH, SCORE_HEIGHT, pix)

        #Post process pixels to determine if "1"
        if(len(white_px) == 8):
            score_temp = 1
            score_x += SCORE_ALT_WIDTH + 1
        else:

            #Otherwise check first 9 pixels if value is "2"-"9"
            white_px = find_white_pixels(SCORE_X_POS + score_x, SCORE_Y_POS, SCORE_HEIGHT, SCORE_HEIGHT, pix)

            #Post process pixels to compare what value
            score_temp = get_score_num(white_px)

            score_x += SCORE_HEIGHT + 1
    
    return curr_score


# Environment Class
class HeliAttackEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    def __init__(self):
        super().__init__()

        # Self Fields


        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(6)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(3, WIDTH, HEIGHT), dtype=np.uint8)
        
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

        # Reset inputs
        pyautogui.keyUp('right')
        pyautogui.keyUp('left')
        pyautogui.keyUp('up')
        pyautogui.keyUp('down')
        pyautogui.mouseUp()

        # Get mouse position
        mouse_x, _ = pyautogui.position()

        # Move Left
        if(action == 0):
            pyautogui.keyDown('left')
        
        # Move Right
        elif(action == 1):
            pyautogui.keyDown('right')

        # Jump
        elif(action == 2):
            pyautogui.keyDown('up')

        # Duck
        elif(action == 3):
            pyautogui.keyDown('down')

        # Move mouse left
        elif(action == 4 and mouse_x > LEFT_LIMIT):
            pyautogui.move(-MOUSE, 0)
        
        # Move mouse right
        elif(action == 5 and mouse_x < RIGHT_LIMIT):
            pyautogui.move(MOUSE, 0)

        # Shoot
        elif(action == 6):
            pyautogui.mouseDown()
        
        # Do nothing (action == 7)


        # Get overall screen
        pix = grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)

        # Get new game score
        last_score = score
        score = get_score(pix)

        # Increase reward each hit
        if(last_score < score):
            reward += 1

        # Larger reward for downing helicopter
        if(score % 30000 == 0 or (score // 30000 > last_score // 30000)):
            reward += 30

        
        # Check health
        last_health = health
        health = get_health(health, pix)

        # Reduce reward if hit
        if(last_health > health):
            reward -= 10

        # End game if dead
        if(health <= 0):
            self.done = True
            reward -= 150

        return self.observation, self.reward, self.done, self.truncated, info

    def reset(self, seed=None, options=None):
        info = {}
        last_score = 0
        score = 0
        last_health = 0
        health = 10

        score_x = 0

        # Reset inputs
        pyautogui.keyUp('right')
        pyautogui.keyUp('left')
        pyautogui.keyUp('up')
        pyautogui.keyUp('down')
        pyautogui.mouseUp()

        # Wait for death screen
        time.sleep(7)

        # Click to open main menu
        pyautogui.moveTo(400, 620)
        pyautogui.click()

        # Click "Start Button"
        pyautogui.moveTo(662, 697)
        pyautogui.click()

        # Move Mouse to Starting Position
        pyautogui.moveTo(480, 328)

        # Wait for paratrooper to land
        time.sleep(3)
        
        # Get overall screen
        pix = grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT)

        return self.observation, info

    # Close File
    def close(self):
        self.file.close()