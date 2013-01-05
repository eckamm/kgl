import os
import sys
import time
import random
import pygame
import glob

from tileboard import TileBoard
from player import Player



if len(sys.argv) > 1:
    num_players = int(sys.argv[1])
else:
    num_players = 1

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sound_dir = os.path.join(base_dir, "sounds")


random.seed(0)

BG_COLOR = (0, 55, 55)
FOOD_COLOR = (255, 0, 0)
OBSTACLE_COLOR = (0, 0, 0)
ENEMY_COLOR = (250, 0, 0)
WORM_COLORS = [
    (0, 255, 0),
    (255, 255, 255),
    (255, 0, 255),
    (0, 255, 255),
]


pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
print "joystick_count:", joystick_count
for joystick_id in range(joystick_count):
    joystick = pygame.joystick.Joystick(joystick_id)
    joystick.init()


pygame.mixer.init()
#eat_sound = pygame.mixer.Sound(os.path.join(sound_dir, "tada.wav"))
#crash_sound = pygame.mixer.Sound(os.path.join(sound_dir, "Windows Critical Stop.wav"))
#x_sound = pygame.mixer.Sound(os.path.join(sound_dir, "Windows Recycle.wav"))
#x_sound.set_volume(0.2)

pygame.font.init()

# Window dimensions.
width = 640
height = 640
width = 900
height = 900
hud_height = 100


class Globalz:
    def __init__(self, 
                 num_players,
                 joystick_count, 
                 surface, 
                 width, height, hud_height,
                 bg_color, food_color, enemy_color, obstacle_color, worm_colors,
                 friendly_crash=False,
                 eat_sound=None):
        self.num_players = num_players
        self.joystick_count = joystick_count
        self.surface = surface
        self.width = width
        self.height = height
        self.hud_height = hud_height
        self.bg_color = bg_color
        self.food_color = food_color
        self.enemy_color = enemy_color
        self.obstacle_color = obstacle_color
        self.worm_colors = worm_colors
        self.friendly_crash = friendly_crash
        self.eat_sound = eat_sound
        self.scores = {}


#screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
screen = pygame.display.set_mode((width, height))
pygame.mouse.set_visible(False)


globalz = Globalz(num_players,
                  joystick_count, 
                  screen, 
                  width, height,
                  hud_height,
                  BG_COLOR, FOOD_COLOR, ENEMY_COLOR, OBSTACLE_COLOR, WORM_COLORS,
                  friendly_crash=False,
                  eat_sound=None)

globalz.images = {}
globalz.images["apple"] = pygame.image.load("kewlapple_64x64.png")
globalz.images["apple"].convert()

tile_filenm_map = {
    "i": "ForceBox.png",
    "f": "WoodFloor.png",
    "g": "GrassFloor.png",
    "G": "GoalTile.png",
    "w": "WoodWall.png",
    "s": "StoneFloor.png",
    "c": "Crate.png",
    "p": "Character.png",
    "I": "ForcePlayer.png",
}
for x, filenm in tile_filenm_map.items():
    globalz.images[x] = pygame.image.load(filenm)
    globalz.images[x].convert()



class TestSprite(pygame.sprite.Sprite):
    def __init__(self, g, pos, size):
        self.g = g
        self.image = pygame.transform.scale(self.g.images["apple"], (size, size))
        self.pos = pos
        self.size = size
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], size, size)
        pygame.sprite.Sprite.__init__(self)

    def draw(self):
        self.g.surface.blit(self.image, self.rect)



def run_game(g, level_filenm):
    g.surface.fill(g.bg_color)
    pygame.display.flip()

#   pgroup = pygame.sprite.GroupSingle()
#   pgroup.add(TestSprite(g, (110, 300), 80))


#   group = pygame.sprite.Group()
#   for i in range(4):
#       group.add(TestSprite(g, (i*100, i*100), 30*i))

#   group.draw(g.surface)
#   pgroup.clear(g.surface, g.bg_color)
    #pgroup.draw(g.surface)
#   pgroup.sprite.draw()

#   for i in (120, 119, 118, 117, 116, 115):
#       pgroup.sprite.rect = pygame.rect.Rect(pgroup.sprite.rect[0], 
#                                             i,
#                                             pgroup.sprite.rect[2], 
#                                             pgroup.sprite.rect[3])
#       print pgroup.sprite.rect[1], pygame.sprite.spritecollide(pgroup.sprite, group, False, pygame.sprite.collide_mask)
#       #pgroup.draw(g.surface)
#       pgroup.sprite.draw()
#       time.sleep(.3)
#       pygame.display.flip()

    clock = pygame.time.Clock()

    tb = TileBoard(g, 100, 100, filenm=level_filenm)

    start = (tb.start[0], tb.start[1], 1)
    player = Player(start)

    tick = 20
    restart = False
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                restart = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    restart = False
                elif event.key == pygame.K_r:
                    running = False
                    restart = True
                elif event.key == pygame.K_n:
                    restart = "next"
                    running = False
                status = player.keyboard_event(event, tb)
                if status == "killed":
                    restart = True
                    running = False
                elif status == "won":
                    restart = "next"
                    running = False

            #print "++", event

        tb.draw(player.tile_loc)
        pygame.display.flip()
        clock.tick(tick)

        pygame.display.set_caption("FPS: %.2f" % (clock.get_fps(),))
    #   x_sound.play()

#   time.sleep(2)

    return restart


if __name__=="__main__":
    level_filenms = sorted(glob.glob("level_*.kgl"))
    level_idx = 0
    while 1:
        level_filenm = level_filenms[level_idx]
        restart = run_game(globalz, level_filenm)
        if restart == "next":
            level_idx += 1
            if level_idx >= len(level_filenms):
                print "No more levels."
                break
        elif restart is False:
            break
    time.sleep(0.5)

