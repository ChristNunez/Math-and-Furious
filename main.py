import pygame
import math
import time
import random
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()


# All the images to be generated on the window(win)
GRASS = scale_image(pygame.image.load('imgs/grass.jpg'), 2.5)
TRACK = scale_image(pygame.image.load('imgs/track.png'), 0.9)

TRACK_BORDER= scale_image(pygame.image.load('imgs/track-border.png'),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)
# Track which flags have been answered correctly
answered_flags = set()
RED = (255, 0, 0)

# Flag 
CHECKPOINT = scale_image(pygame.image.load('imgs/checkpoint.png'), 0.025)

RED_CAR = scale_image(pygame.image.load('imgs/red-car.png'),0.55)
GREEN_CAR = scale_image(pygame.image.load('imgs/green-car.png'),0.55)


# Width and height of the game window
WITDH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WITDH, HEIGHT))
pygame.display.set_caption("Math and Furious!")

MAIN_FONT = pygame.font.SysFont("Consolas", 44)

FPS = 60
PATH = [(168, 101), (104, 74), (44, 141), (64, 484), (346, 732), (412, 664), (414, 520), (494, 476), 
        (585, 514), (613, 722), (739, 716), (732, 384), (586, 354), (406, 339), (428, 257), (728, 240), 
        (737, 110), (600, 71), (291, 80), (262, 368), (180, 380), (150, 260)]

# Math portion of the game 
# Flag positions
FLAG_POSITIONS = [(10, 200), (248, 725), (685, 585), (615, 15)]
FLAG_TRIGGER_DISTANCE = 80

# Math question state
current_question = None
correct_answer = None
user_input = ""
feedback = ""
active_flag = None

# Level system for the game
class GameInfo:
    LEVELS = 5

    def __init__(self, level = 1):
        self.level = level
        self.start_game = False
        self.level_start_time = 0 

    def next_level(self):
        self.level += 1
        self.start_game = False

    def reset(self):
        self.level = 1
        self.start_game = False
        self.level_start_time = 0

    def end_game(self):
        return self.level > self.LEVELS
    
    def start_level(self):
        self.start_game = True
        self.level_start_time = time.time()

    def get_level_time(self): 
        if not self.start_game:
            return 0
        return round(time.time() - self.level_start_time)

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

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    win.blit(CHECKPOINT,(10,200))
    win.blit(CHECKPOINT,(248,725))
    win.blit(CHECKPOINT,(685,585))
    win.blit(CHECKPOINT,(615,15))


    level_text = MAIN_FONT.render(f"Level {game_info.level}",1,(255,255,255))
    win.blit(level_text, (10, HEIGHT- level_text.get_height() - 70))


    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s",1,(255,255,255))
    win.blit(time_text, (10, HEIGHT- time_text.get_height() - 40))


    vel_text = MAIN_FONT.render(f"Speed: {round(player_car.vel), 1}f/s",1,(255,255,255))
    win.blit(vel_text, (10, HEIGHT- vel_text.get_height() - 10))

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

def car_collisions(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()


    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        blit_text_center(WIN, MAIN_FONT, "You lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.next_level(1)
        answered_flags.clear()


    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)
            answered_flags.clear()


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def generate_question():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(['+', '-'])
    question = f"{a} {op} {b} = ?"
    answer = a + b if op == '+' else a - b
    return question, answer


run = True
clock = pygame.time.Clock()
images = [(GRASS,(0,0)), (TRACK,(0,0)), 
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]

# Velocities, straight line and rotaional, for both the player car and the computer car 
player_car = PlayerCar(4,4) 
computer_car = ComputerCar(1,1, PATH)
game_info = GameInfo()


# Main event loop
while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, game_info)

    while not game_info.start_game:
        blit_text_center(
            WIN, MAIN_FONT,f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

        '''
        #TO FIND THE COMPUTER CARS PATH FOR THE MULTIPLE TRACKS
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            print(pos)
            #computer_car.path.append(pos)
        '''

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        # --- Handle typing for math answers ---
        if current_question and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    if int(user_input) == correct_answer:
                        feedback = "✅ Correct!"
                    else:
                        feedback = "❌ Try again!"
                except ValueError:
                    feedback = "Enter a number!"
                user_input = ""
            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            elif event.unicode.isdigit() or (event.unicode == '-' and not user_input):
                user_input += event.unicode


    # Only allow movement if there’s no active question or it’s been answered correctly
    if current_question is None or "Correct" in feedback:
        player_moves(player_car)

    computer_car.move()

    car_collisions(player_car, computer_car, game_info)

    # --- Check if player is close to any flag ---
    near_flag = None
    for pos in FLAG_POSITIONS:
        if distance(player_car.x, player_car.y, pos[0], pos[1]) < FLAG_TRIGGER_DISTANCE:
            near_flag = pos
            break

    # --- Show question if near a flag and not answered yet ---
    if near_flag and near_flag not in answered_flags:
        # Freeze car while answering
        player_car.vel = 0

        if current_question is None or active_flag != near_flag:
            current_question, correct_answer = generate_question()
            feedback = ""
            user_input = ""
            active_flag = near_flag

        # Draw the math question (higher on screen)
        q_text = MAIN_FONT.render(current_question, True, (255, 255, 255))
        WIN.blit(q_text, (WITDH // 2 - q_text.get_width() // 2, 50))

        ans_text = MAIN_FONT.render(user_input, True, (255, 255, 0))
        WIN.blit(ans_text, (WITDH // 2 - ans_text.get_width() // 2, 100))

        fb_text = MAIN_FONT.render(feedback, True, (0, 255, 0) if "Correct" in feedback else (255, 0, 0))
        WIN.blit(fb_text, (WITDH // 2 - fb_text.get_width() // 2, 150))

        # If answered correctly, unlock movement and mark flag as done
        if "Correct" in feedback:
            answered_flags.add(near_flag)
            current_question = None
            feedback = ""
            user_input = ""
            active_flag = None

    else:
        current_question = None
        feedback = ""
        user_input = ""
        active_flag = None



    #pygame.draw.line(WIN, RED, (200, 300), (600, 300), 5)
    pygame.display.update()


    if game_info.end_game():
        blit_text_center(WIN, MAIN_FONT, "You Won the Game!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.next_level(1)
        answered_flags.clear()

#print(pos)
pygame.quit()
