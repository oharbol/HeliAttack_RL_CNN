from PIL import ImageGrab
from datetime import datetime
import time
import pyautogui
import cv2
import numpy as np


health = 10
health_y_list = [6,11,21,30,40,50,60,70,79,89]
last_health = health

last_score = 0
score_x = 0
score_last = -1
score = 0
score_temp = -1
SCORE_X_POS = 58
SCORE_Y_POS = 23

SCREEN_X = 198
SCREEN_Y = 328
SCREEN_WIDTH = 563
SCREEN_HEIGHT = 378

#Takes screen shot of designated area
#Automatically does not save screen shot
def grab_screenshot(x,y,x2,y2,save=False, name="Test"):
    im = ImageGrab.grab([x, y, x2, y2])
    pix = im.load()

    # Read image with opencv
    # img = np.asarray(im)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # BandW = im.convert('1')
    # BandW.save("Test Images/BandW3_Dirty.png")
    # thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # cv2.imwrite("Test Images/Gray3_Clear_Dirty.png", thresh)

    #Save Image
    if(save):
        #Temp data for saving images
        dt = datetime.now()
        fname = f"Test Images/{name}.png"
        im.save(fname, 'png')

    return pix

#Switch Case to get current score
def get_score(list_pix):
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
            return 4
        case _:
            return -1

#Translate Score Letter Pixels to list of white pixels in image
#Temporary list to hold white pixel locations
def find_white_pixels(start_x, start_y, x_pix, y_pix, pixels):
    im = ImageGrab.grab([start_x, start_y, start_x + x_pix, start_y + y_pix])
    fname = f"Test Images/{x_pix}{y_pix}.png"
    im.save(fname, 'png')
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


# pixel_0 = [[1,2], [7,2], [1,3], [7,3], [1,4], [7,4], [1,5], [7,5], [1,6], [7,6]]
# pixel_1 = [[2,1], [2,2], [2,3], [2,4], [2,5], [2,6], [2,7], [2,8]]
# pixel_2 = [[7,2], [7,3], [1,7], [1,8]]
# pixel_3 = [[7,2], [7,3], [7,6]]
# pixel_4 = [[4,1], [5,1], [6,1], [6,2], [6,3], [6,4], [1,5], [6,5], [6,6], [6,7], [6,8]]
pixel_5 = [[1,1], [1,2], [1,3], [1,4], [7,6]]
pixel_6 = [[1,2], [1,3], [1,4], [1,5], [1,6], [7,6]]
# pixel_7 = [[7,1], [4,5], [5,5], [3,7], [3,8]]
# pixel_8 = [[1,2], [7,2], [1,3], [7,3], [1,6], [7,6]]
# pixel_9 = [[1,2], [7,2], [1,3], [7,3], [7,4], [7,5], [7,6]]

#10: #0 g
#8 : #1 g
#4 : #2 g
#3 : #3 g
#11: #4 
#5 : #5 #7 g
#6 : #6 #8 g
#7 : #9 g

print("Health: ", health)

while health > 0:
    #Get cropped image of game
    #im = ImageGrab.grab([678, 323, 1242, 702])
    # im = ImageGrab.grab([198, 328, 761, 706])
    # pix = im.load()

    #Take screenshot of entire area
    pix = grab_screenshot(SCREEN_X, SCREEN_Y, SCREEN_X + SCREEN_WIDTH, SCREEN_Y + SCREEN_HEIGHT)

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
    # if(health != last_health):
    #     print("Health: ", health)
    #     last_health = health



    #Score Test Code
    #Score
    #Top Left 58 23
    #Bottom Right 66 31
    #All numbers 9x9 px, "1" is 4x9 px
    score_square = 9
    score_1_width = 4
    score = 0
    score_temp = -1


    #//////////////////

    while score_temp != 0:
        #Check first 4 pixels if image is one
        #pixels = grab_screenshot(SCREEN_X + SCORE_X_POS + score_x, SCREEN_Y + SCORE_Y_POS, SCREEN_X + SCORE_X_POS + score_square + score_x, SCREEN_Y + SCORE_Y_POS + score_square, save=True, name="1Check")
        white_px = find_white_pixels(SCORE_X_POS + score_x, SCORE_Y_POS, score_1_width, score_square, pix)


        #Post process pixels to determine if "1"
        if(len(white_px) == 8):
            score_temp = 1
            score_x += score_1_width + 1
        else:

            #Otherwise check first 9 pixels if value is "2"-"9"
            #pixels = grab_screenshot(SCREEN_X + SCORE_X_POS + score_x, SCREEN_Y + SCORE_Y_POS, SCREEN_X + SCORE_X_POS + score_square + score_x, SCREEN_Y + SCORE_Y_POS + score_square, save=True, name="otherCheck")
            #white_px = find_white_pixels(SCREEN_X + SCORE_X_POS + score_x, SCREEN_Y + SCORE_Y_POS, score_square, score_square, pix)
            white_px = find_white_pixels(SCORE_X_POS + score_x, SCORE_Y_POS, score_square, score_square, pix)

            #Post process pixels to compare what value
            score_temp = get_score(white_px)

            score_x += score_square + 1

        #Loop until zero is found, concat letters, to int, multiply by 1000
        if(score_temp == 0):
            score = score * 1000
        else:
            score = (score * 10) + score_temp

    #Multiply temp score by 10, add found value
    #Print score for now
    if(score != score_last):
        print("Score: ", score)
        score_last = score


    #Reset score_x
    score_x = 0


#Movement Notes
#Main Menu: X 662 Y 697
#Starting Mouse: X 480 Y 328

#Movement Testing code
# pyautogui.moveTo(662, 697)
# pyautogui.click()
# pyautogui.moveTo(480, 328)

# Hold down the 'shift' key
#pyautogui.keyDown('shift')


#End of Game
print("You died! You suck!")



# HEALTH CODE #


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