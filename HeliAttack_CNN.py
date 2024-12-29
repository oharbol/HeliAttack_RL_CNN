from PIL import ImageGrab
from datetime import datetime
import time

health = 10
health_y_list = [6,11,21,30,40,50,60,70,79,89]
last_health = health

#Health - 10 hits approx. 9 px per hit
#Top: X 547 Y 6
#Bottom: X 547 Y 93
#Main Menu: X 464 Y 369

#Score
#Top Left 58 23
#Bottom Right 66 31
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

print("Health: ", health)

# while health > 0:
#Get cropped image of game
#im = ImageGrab.grab([678, 323, 1242, 702])
im = ImageGrab.grab([198, 328, 761, 706])
pix = im.load()

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

#Temp data for saving images

dt = datetime.now()
fname = "Test Images/pic_{}.{}.png".format(dt.strftime("%H%M_%S"), dt.microsecond // 100000)
im.save(fname, 'png')

print("You died! You suck!")