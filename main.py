import pgzrun
from random import randint, random

WIDTH = 1280
HEIGHT = 720
GRAVITY = 0.3
GAP = 400
SCROLL_SPEED = 1200
JUMP_STRENGTH = 12
BUILDING_WIDTH = 1200 * 2
BUILDING_HEIGHT = 992

game_state = "menu"
city_x = 0
city_w = 1440 * 2
score = 0
play_sounds = True

sounds.music.play(-1)
sounds.music.set_volume(0.3)

def get_random_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def change_game_state(new_state):
    global game_state
    game_state = new_state


class Button():
    def __init__(self, text, x, y, w, h, callback):
        self.rect = Rect((x, y), (w, h))
        self.text = text
        self.color = get_random_color()
        self.callback = callback

    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=40, color=(0, 0, 0))

def toggle_music():
    global play_sounds
    if play_sounds:
        sounds.music.stop()
        play_sounds = False
    else:
        sounds.music.play(-1)
        play_sounds = True

btn_start = Button("Start", WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50, lambda: change_game_state("game"))
btn_toggle_music = Button("Toggle Sound", WIDTH // 2 - 100, HEIGHT // 2 + 75, 200, 50, lambda: toggle_music())
btn_exit = Button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 175, 200, 50, lambda: exit())
menu_buttons = [btn_start, btn_toggle_music, btn_exit]

NUM_BUILDINGS = 2
buildings = []

def on_mouse_up(pos):
    if game_state == "menu":
        for button in menu_buttons:
            if button.rect.collidepoint(pos):
                button.callback()
    elif game_state == "gameover":
        if btn_exit.rect.collidepoint(pos):
            exit()


class Building():
    def __init__(self, x, y, w, h):
        self.original_pos = (x, y)
        self.rect = Rect((x, y), (w, h))
        self.image = "building2x.png"
        self.has_obstacle = False
        self.obstacle = Rect((0, 0), (64, 138))

    def draw(self):
        screen.blit(self.image, self.rect)
        if self.has_obstacle:
            self.obstacle.x = self.rect.x + (self.rect.w - self.obstacle.width) // 2
            self.obstacle.y = self.rect.y - self.obstacle.height
            screen.blit("barrel.png", (self.obstacle.x, self.obstacle.y))


class Hero(Actor):
    def __init__(self):
        super().__init__("bob/run/1.png")

        self.images = {
            "run": ["bob/run/"+f"{i}.png" for i in range(1, 11)],
            "jump": ["bob/jump/"+f"{i}.png" for i in range(1, 9)],
        }

        self.x = WIDTH // 8
        self.y = HEIGHT // 8
        self.w = 60
        self.h = 41
        self.vel_y = 0
        self.frame = 0
        self.frame_timer = 0
        self.frame_interval = 0.04
        self.is_on_ground = False
        self.state = "jump"

    def jump(self):
        if self.is_on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.is_on_ground = False
            self.state = "jump"
            self.frame = 0

            if play_sounds:
                sounds.jump.play()

    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_interval:
            self.frame_timer = 0
            self.next_image()

        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self._rect.collidelist(buildings) == -1:
            self.is_on_ground = False
            self.state = "jump"
        else:
            for b in buildings:
                if self._rect.colliderect(b.rect):
                    if self.vel_y > 0 and self.y + self.h <= b.rect.y + self.vel_y:
                        self.vel_y = 0
                        self.is_on_ground = True
                        self.y = b.rect.y - self.h
                        self.state = "run"

        if self.y >= HEIGHT:
            change_game_state("gameover")
            return

        if self.vel_y != 0:
            self.state = "jump"

    def next_image(self):
        self.frame = (self.frame + 1) % (10 if self.state == "run" else 8)
        self.image = self.images[self.state][self.frame]

bob = Hero()

for i in range(NUM_BUILDINGS):
    x = i * BUILDING_WIDTH + i * GAP
    y = HEIGHT // 2 - (random() * -150 if random() < 0.5 else random() * 150)
    buildings.append(Building(x, y, BUILDING_WIDTH, BUILDING_HEIGHT))

import time
last_time = time.time()
def update():
    global last_time, city_x, game_state, score
    dt = time.time() - last_time
    last_time = time.time()
    
    scroll = SCROLL_SPEED * 2 if keyboard.lshift else SCROLL_SPEED

    if game_state == "game":
        city_x -= dt * scroll / 4
        score += dt * scroll / 32
        scroll = scroll

        if city_x <= -city_w:
            city_x = 0

        if keyboard.escape:
            if game_state == "menu":
                exit()
            else:
                change_game_state("menu")
        elif keyboard.space:
            bob.jump()
        
        bob.update(dt)

        for b in buildings:
            b.rect.x -= dt * scroll
            
            if b.has_obstacle and bob._rect.colliderect(b.obstacle):
                change_game_state("gameover")

            if b.rect.right <= 0:
                max_right = max(other.rect.x + other.rect.w for other in buildings)
                b.rect.x = max_right + GAP
                b.rect.y = HEIGHT // 2 - (random() * -150 if random() < 0.5 else random() * 150)
                b.has_obstacle = random() < 0.3


def draw():
    if game_state == "menu":
        screen.fill((0, 0, 0))
        for button in menu_buttons:
            button.draw()

    elif game_state == "game":
        screen.blit("city.png", (city_x, 0)) # type: ignore
        screen.blit("city.png", (city_x + city_w, 0))

        for b in buildings:
            b.draw()
        bob.draw()

        screen.draw.text(f"Distance: {int(score)}", (10, 10), fontsize=40, color=(255, 255, 255))
    
    elif game_state == "gameover":
        screen.fill((0, 0, 0))
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=80, color=(255, 0, 0))
        screen.draw.text(f"Distance: {int(score)}", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color=(255, 255, 255))
        btn_exit.draw()

pgzrun.go()
