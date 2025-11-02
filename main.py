import pygame
import math
import time
from utils import scale_image, blit_rotate_center


GRASS = scale_image(pygame.image.load('imgs/grass.jpg'), 2.5)
TRACK = scale_image(pygame.image.load('imgs/track.png'), 0.9)

TRACKBORDER= scale_image(pygame.image.load('imgs/track-border.png'),0.9)
FINISH = pygame.image.load('imgs/finish.png')

RED_CAR = scale_image(pygame.image.load('imgs/red-car.png'),0.55)
GREEN_CAR = scale_image(pygame.image.load('imgs/green-car.png'),0.55)


# Width and height of the game window
WITDH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WITDH, HEIGHT))
pygame.display.set_caption("Math and Furious!")

FPS = 60

# For both player and AI cars
class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1


    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

# Defined the image to inherit from AbstractCar
class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS =(180, 200)

def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    pygame.display.update()

run = True
clock = pygame.time.Clock()
images = [(GRASS,(0,0)), (TRACK,(0,0))]
player_car = PlayerCar(4,4) # The velocity of the car and rotation velocity
player_car = PlayerCar(4,4)


# Main event loop
while run:
    clock.tick(FPS)

    draw(WIN, images, player_car)
    pygame.display.update()

     # Event loop to check for quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)   
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()

    if not moved:
        player_car.reduce_speed()

pygame.quit()





# Math logic for generating questions and checking answers
"""
import random

# Addition Function
def add_value(addx, addy):
    add_total = addx + addy
    return add_total

# Subtraction Function
def sub_value(subx, suby):
    sub_total = subx - suby
    return sub_total

def multiply_value(mulx, muly):
    mul_total = mulx * muly
    return mul_total

def divide_value(divx, divy):
    div_total = divx / divy
    return div_total    

# Main Game Loop
run_game = input("Do you want to play a math game? (yes/no) ").lower()
while(run_game == "yes"):
    # Addition and Subtraction Random Numbers
    addx = random.randint(1, 10)
    addy = random.randint(1, 10)
    subx = random.randint(1, 10)
    suby = random.randint(1, 10)

    # Multiplication and Division Random Numbers
    mulx = random.randint(1, 10)
    muly = random.randint(1, 10)
    divx = random.randint(1, 100)
    divy = random.randint(1, 10)

    add_value(addx, addy)
    sub_value(subx, suby)
    multiply_value(mulx, muly)
    divide_value(divx, divy)

    player_choice_add = int(input(f"What is the value of {addx} + {addy}? "))
    player_choice_sub = int(input(f"What is the value of {subx} - {suby}? "))
    player_choice_mul = int(input(f"What is the value of {mulx} * {muly}? "))
    player_choice_div = float(input(f"What is the value of {divx} / {divy}? "))

    if (player_choice_add != add_value(addx, addy)):
        print(f"Incorrect, The answer to {addx} + {addy} is {add_value(addx, addy)}")
    else:
        print(f"Correct! The answer to {addx} + {addy} is {add_value(addx, addy)}")

    if (player_choice_sub != sub_value(subx, suby)):
        print(f"Incorrect, The answer to {subx} + {suby} is {sub_value(subx, suby)}")
    else:
        print(f"Correct! The answer to {subx} - {suby} is {sub_value(subx, suby)}")
    if (player_choice_mul != multiply_value(mulx, muly)):
        print(f"Incorrect, The answer to {mulx} * {muly} is {multiply_value(mulx, muly)}")
    else:
        print(f"Correct! The answer to {mulx} * {muly} is {multiply_value(mulx, muly)}")
    if (player_choice_div != divide_value(divx, divy)):
        print(f"Incorrect, The answer to {divx} / {divy} is {divide_value(divx, divy)}")
    else:
        print(f"Correct! The answer to {divx} / {divy} is {divide_value(divx, divy)}")

    run_game = input("Do you want to play a math game? (yes/no) ").lower()

    """