from PIL import ImageGrab
from datetime import datetime
import time
import pyautogui
import cv2
import numpy as np


health = 10
health_y_list = [6,11,21,30,40,50,60,70,79,89]
last_health = health

SCREEN_X = 198
SCREEN_Y = 328
SCREEN_WIDTH = 563
SCREEN_HEIGHT = 378

#Takes screen shot of designated area
#Automatically does not save screen shot
def grab_screenshot(x,y,x2,y2,save=False):
    im = ImageGrab.grab([x, y, x2, y2])
    pix = im.load()

    # Read image with opencv
    img = np.asarray(im)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    BandW = im.convert('1')

    BandW.save("Test Images/BandW3_Dirty.png")

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    cv2.imwrite("Test Images/Gray3_Clear_Dirty.png", thresh)

    #Save Image
    if(save):
        #Temp data for saving images
        dt = datetime.now()
        fname = "Test Images/3_Clear_Dirty.png"
        im.save(fname, 'png')

    return pix

#Health - 10 hits approx. 9 px per hit
#Top: X 547 Y 6
#Bottom: X 547 Y 93

#               Red Pixels      White/Gray Pixels

#0 HIT: 6 px    (245, 42, 33)   (165, 165, 165)
#1 HIT: 11 px   (249, 139, 114) (203, 203, 203)
#2 HIT: 21 px   (253, 78, 58)   (207, 207, 207)
#3 HIT: 30 px   (255, 74, 53)   (204, 204, 204)
#4 HIT: 40 px   (255, 74, 53)   (204, 204, 204)
#5 HIT: 50 px   (255, 74, 53)   (204, 204, 204)
#6 HIT: 60 px   (255, 71, 51)   (204, 204, 204)
#7 HIT: 70 px   (255, 48, 35)   (202, 202, 202)
#8 HIT: 79 px   (255, 71, 55)   (186, 186, 186)
#9 HIT: 89 px   (255, 85, 89)   (194, 194, 194)

#Take screenshot of entire area
pix = grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + SCREEN_WIDTH, SCREEN_Y + SCREEN_HEIGHT)

print("Health: ", health)

#Health handling code

# while health > 0:
#Get cropped image of game
#im = ImageGrab.grab([678, 323, 1242, 702])
# im = ImageGrab.grab([198, 328, 761, 706])
# pix = im.load()

#Get colored pixel of health at last red level
color = pix[552, health_y_list[10 - health]]

#Player was hit
#If white/gray pixel is observed reduce heath
if(color[0] == color[1]):
    health -= 1

#Check if med pack was picked up
if(health == 9):
    #Get colored pixel at space 10
    color = pix[552, health_y_list[0]]
    if(color[0] > color[1] and color[1] != color[2]):
        health += 1
elif(health < 9):
    #Get colored pixel at space above 2 health levels
    color = pix[552, health_y_list[8 - health]]
    if(color[0] > color[1] and color[1] != color[2]):
        health += 2

#DEBUGGING CODE#
#Print health each time player gets hit or gets medpack
if(health != last_health):
    print("Health: ", health)
    last_health = health

#Score Test Code
#Score
#Top Left 58 23
#Bottom Right 66 31
#All numbers 9x9 px, "1" is 4x9 px
score_square = 9
score_1_width = 4

#Check first 4 pixels if image is one
#grab_screenshot(SCREEN_X + 58, SCREEN_Y + 23, SCREEN_X + 58 + score_1_width, SCREEN_Y + 23 + score_square, save=True)

#Post process pixels to determine if "1"

#Otherwise check first 9 pixels if value is "2"-"9"
grab_screenshot(SCREEN_X + 58, SCREEN_Y + 23, SCREEN_X + 58 + score_square, SCREEN_Y + 23 + score_square, save=True)

#Post process pixels to compare what value

#Multiply temp score by 10, add found value

#Loop until zero is found, concat letters, to int, multiply by 1000




#Movement Notes
#Main Menu: X 662 Y 697
#Starting Mouse: X 480 Y 328

#Movement Testing code
# pyautogui.moveTo(662, 697)
# pyautogui.click()
# pyautogui.moveTo(480, 328)

#End of Game
print("You died! You suck!")