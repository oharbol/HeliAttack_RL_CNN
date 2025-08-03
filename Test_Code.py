from PIL import ImageGrab
import time
import pynput
from pynput.mouse import Button
from pynput.keyboard import Key



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

WHITE_PIX = (255, 255, 255)
WHITE_RED_PIX = (255, 254, 254)

health = 10

# Method to determine current score
def get_score(pix):
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

def get_health(pix, health):
    if(health == 1):
        y = 67
    else:
        y = 2 + (10 - health) * 8
    x = 3

    # print("x,y", x, y)
    # print(pix[x,y])

    #Player hit
    if(pix[x,y] == WHITE_PIX or pix[x,y] == WHITE_RED_PIX):
        health -= 1

    #Medpack picked up
    elif(health == 9 and pix[x,y-8] != WHITE_PIX and pix[x,y-8] != WHITE_RED_PIX):
        health += 1

    #Health less than 9
    elif(health < 9 and pix[x,y-16] != WHITE_PIX and pix[x,y-16] != WHITE_RED_PIX):
        #print(pix[x,y-16])
        health += 2

    # print(pix[x,y] == WHITE_PIX or pix[x,y] == WHITE_RED_PIX)
    return health


im = ImageGrab.grab([SCREEN_X, SCREEN_Y, SCREEN_X + WIDTH, SCREEN_Y + HEIGHT])
im.save("Test.png")
pix = im.load()
# print(pix[2,4])
health = get_health(pix, health)
print("HEALTH: ", health)
    


# gray_pix = im.convert("L")
# gray_pix = gray_pix.load()
# print(gray_pix[X,Y])

# SCREEN_X = 254 #198
# SCREEN_Y = 370 #328
# WIDTH = 452
# HEIGHT = 322

### WORKS!!!! ###
# score = get_score(pix)
# print(score)

# Health
