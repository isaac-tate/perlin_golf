import noise
import numpy as np
from PIL import Image
from random import randint
import pygame
import os
import math

shape = (900, 512)
scale = 300.0
octaves = 2
persistence = 0.6
lacunarity = 1000.0

ball_location = (0, 0)
target_location = (0, 0)
flag_location = (0, 0)


def generate_course():
    #Set random values
    seed = randint(10000000, 99999999)

    fairway_radias = randint(70, 90)
    water_ratio = randint(10, 50)/100
    sand_ratio = randint(10, 30)/100

    #Empty world
    world = np.zeros(np.zeros(shape).shape+(3,))

    #Fairway noise
    fairway_map = np.zeros(shape)
    fairway_range = (shape[1]//10, ((shape[1]//10)*9))

    fairway_point = None
    green_point = None

    for i in range(150, shape[0]-50):

        fairway_point = (noise.pnoise2((i+seed)/scale, 
                                    (i+seed)/scale, 
                                    octaves=octaves, 
                                    persistence=persistence, 
                                    lacunarity=lacunarity, 
                                    repeatx=1024, 
                                    repeaty=1024, 
                                    base=0) + 0.5) * (fairway_range[1] - fairway_range[0]) + fairway_range[0]

        for j in range(int(fairway_point)-fairway_radias, int(fairway_point+fairway_radias)):
            try:
                fairway_map[i][j] = 1
            except:
                pass

        if green_point == None:
            green_point = fairway_point

    #Draw green
    print("FAIRWAY POINT", green_point)

    a, b = 150, int(green_point)
    r = 60
    EPSILON = 100

    for x in range(shape[1]):
        for y in range(shape[0]):
            if abs((x-a)**2 + (y-b)**2 - r**2) < EPSILON**2:
                #print("FAIRWAY", x, y)
                fairway_map[x][y] = 1


    #Sand trap noise
    sand_map = np.zeros(shape)
    for i in range(0, shape[0]):
        for j in range(shape[1]):
            sand_point = noise.pnoise2((i+seed)/scale, 
                                        (j+seed)/scale, 
                                        octaves=octaves, 
                                        persistence=persistence, 
                                        lacunarity=lacunarity, 
                                        repeatx=1024, 
                                        repeaty=1024, 
                                        base=0) + 0.5

            if sand_point < sand_ratio:
                sand_map[i][j] = 1

    #Water noise
    water_map = np.zeros(shape)
    for i in range(0, shape[0]):
        for j in range(shape[1]):
            water_point = noise.pnoise2((i+seed+234)/scale, 
                                        (j+seed+443)/scale, 
                                        octaves=octaves, 
                                        persistence=persistence, 
                                        lacunarity=lacunarity, 
                                        repeatx=1024, 
                                        repeaty=1024, 
                                        base=0) + 0.5

            if water_point < 0.35:
                water_map[i][j] = 1

    #Colour map
    for i in range(shape[0]):
        for j in range(shape[1]):
            if fairway_map[i][j] == 1:
                world[i][j] = (0, 200, 0)
            elif sand_map[i][j] == 1:
                world[i][j] = [244, 220, 181]
            elif water_map[i][j] == 1:
                world[i][j] = [0, 0, 200]
            else:
                world[i][j] = [0, 100, 0]


    return [world, (fairway_point, shape[0]-50), (a, b)]

def place_ball(x, y):
    screen.blit(golf_ball, (x, y))

def draw_line(x_ball, y_ball, x_target, y_target, power):

    og_hypot = math.sqrt((abs(x_ball-x_target)**2) + (abs(y_ball-y_target)**2))

    if og_hypot < power:
        pygame.draw.line(screen, (255, 255, 255), (x_ball, y_ball), (x_target, y_target), 3)
        return (x_target, y_target)
    else:
        try:

            # The desired length of the line is a maximum of 10
            final_len = min(og_hypot, power)

            # figure out how much of the line you want to draw as a fraction
            ratio = 1.0 * final_len / og_hypot

            # Adjust your second point
            x2 = x_ball + (x_target - x_ball) * ratio
            y2 = y_ball + (y_target - y_ball) * ratio

            pygame.draw.line(screen, (255, 255, 255), (x_ball, y_ball), (x2, y2), 3)

            return (x2, y2)

        except Exception as e:
            print(e)

def move_ball(x_ball, y_ball, x_target, y_target, power):

    og_hypot = math.sqrt((abs(x_ball-x_target)**2) + (abs(y_ball-y_target)**2))


    try:

        # The desired length of the line is a maximum of 10
        final_len = min(og_hypot, power)

        # figure out how much of the line you want to draw as a fraction
        ratio = 1.0 * final_len / og_hypot

        # Adjust your second point
        x2 = x_ball + (x_target - x_ball) * ratio
        y2 = y_ball + (y_target - y_ball) * ratio

        place_ball(x2, y2)
        return (x2, y2)

    except Exception as e:
        print(e)

def draw_powerbar(power):

    x_position = 0
    y_position = shape[0]-50

    #pygame.draw.rect(screen, (0, 0, 0), (x_position, y_position, 150, 50), border_width)

    normal_power = (power*shape[1])/100

    if power>0:
        pygame.draw.rect(screen, (255, 0, 0), (x_position, y_position, x_position+normal_power, 50))

def draw_flag(x, y):
    screen.blit(golf_flag, (x, y))


def new_hole():

    this_map = generate_course()
    img = Image.fromarray(np.uint8(this_map[0]), 'RGB')
    bg = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

    current_power = 0

    shooting = False
    shooting_increase = True

    ball_location = (this_map[1][0], this_map[1][1]-25)

    running = True

    while running:

    #Listeners
        for event in pygame.event.get():
            screen.blit(bg, (0, 0))
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                shooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                print("SHOOT")
                shooting = False
                ball_location = move_ball(ball_location[0], ball_location[1], target_location[0], target_location[1], (current_power/130)*200)
                current_power = 0

        if shooting == True:
            if current_power == 100 or current_power == -1:
                shooting_increase = not shooting_increase
            if shooting_increase == True:
                current_power = current_power + 1
            if shooting_increase == False:
                current_power = current_power - 1

        if (ball_location[0] in range(this_map[2][1]-32, this_map[2][1] + 32))\
            and (ball_location[1] in range(this_map[2][0]-32, this_map[2][0]+32)):

            txt = myfont.render("Nice", False, (255, 255, 255))

            screen.blit(txt, (shape[1]/3, shape[0]/3))

            pygame.display.flip()
            new_hole()
            running=False



        #Draw course background
        screen.blit(bg, (0, 0))

        #Draw ball
        #draw_flag()
        place_ball(ball_location[0], ball_location[1])
        draw_flag(this_map[2][1], this_map[2][0])

        #Draw club line
        mousePos = pygame.mouse.get_pos()
        target_location = draw_line(ball_location[0]+12, ball_location[1]+12, mousePos[0], mousePos[1], 200)

        #draw power bar
        draw_powerbar(current_power)

        pygame.display.flip()




#Pygame setup
pygame.init()
myfont = pygame.font.SysFont("Comic Sans MD", 100)

screen = pygame.display.set_mode([shape[1], shape[0]])
running = True

#Load images
golf_ball = pygame.image.load("Code/Test Projects/Golf/assets/golf-ball-24.png")
golf_flag = pygame.image.load("Code/Test Projects/Golf/assets/golf-flag-32.png")

new_hole()