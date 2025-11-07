import pygame
import math
import time
from utils import scale_image, blit_rotate_center


# All the images to be generated on the window(win)
GRASS = scale_image(pygame.image.load('imgs/grass.jpg'), 2.5)
TRACK = scale_image(pygame.image.load('imgs/track.png'), 0.9)

TRACK_BORDER= scale_image(pygame.image.load('imgs/track-border.png'),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load('imgs/red-car.png'),0.55)
GREEN_CAR = scale_image(pygame.image.load('imgs/green-car.png'),0.55)


# Width and height of the game window
WITDH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WITDH, HEIGHT))
pygame.display.set_caption("Math and Furious!")

FPS = 60
PATH = [(168, 101), (104, 74), (44, 141), (64, 484), (346, 732), (412, 664), (414, 520), (494, 476), 
        (585, 514), (613, 722), (739, 716), (732, 384), (586, 354), (406, 339), (428, 257), (728, 240), 
        (737, 110), (600, 71), (291, 80), (262, 368), (180, 380), (150, 260)]

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
    
    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x),int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi
    
    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


# Defined the image to inherit from AbstractCar
class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS =(180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel # gets stuck in weird ways if dividing by number > 1
        self.move

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)


    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel
    
    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255,0,0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else: 
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()


def draw(win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def player_moves(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)   
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def car_collisions(player_car, computer_car):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()


    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        player_car.reset()
        computer_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()
            computer_car.reset()


run = True
clock = pygame.time.Clock()
images = [(GRASS,(0,0)), (TRACK,(0,0)), 
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]

# Velocities, straight line and rotaional, for both the player car and the computer car 
player_car = PlayerCar(4,4) 
computer_car = ComputerCar(2,2, PATH)


# Main event loop
while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car)
    pygame.display.update()

     # Event loop to check for quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        '''
        #TO FIND THE COMPUTER CARS PATH FOR THE MULTIPLE TRACKS
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            computer_car.path.append(pos)
        '''

    player_moves(player_car)
    computer_car.move()

    car_collisions(player_car, computer_car)


#print(computer_car.path)
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