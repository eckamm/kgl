import os
import sys
import time
import random
import pygame
import glob

from tileboard import TileBoard
from player import Player
from leveltitle import LevelTitle
from levelmanager import LevelManager
from modalmessage import ModalMessage, BadModalMessage, GoodModalMessage
from hud import HUD



if len(sys.argv) > 1:
    num_players = int(sys.argv[1])
else:
    num_players = 1

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sound_dir = os.path.join(base_dir, "sounds")


random.seed(0)

BG_COLOR = (0, 55, 55)

pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
print >>sys.stderr, "joystick_count:", joystick_count
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
width = 660   # the height of the display not including the hud at the bottom
height = 660   # we want a square play area (not including the hud)
hud_height = 100
mode_options = pygame.FULLSCREEN

if True:
    width = 520   # the height of the display not including the hud at the bottom
    height = 520   # we want a square play area (not including the hud)
    hud_height = 50
    mode_options = 0


class Globalz:
    def __init__(self, 
                 num_players,
                 joystick_count, 
                 surface, 
                 width, height, hud_height,
                 bg_color,
                 friendly_crash=False,
                 eat_sound=None):
        self.num_players = num_players
        self.joystick_count = joystick_count
        self.surface = surface
        self.width = width
        self.height = height   # the height of the display not including the hud at the bottom
        self.hud_height = hud_height
        self.bg_color = bg_color
        self.friendly_crash = friendly_crash
        self.eat_sound = eat_sound
        self.scores = {}


screen = pygame.display.set_mode((width, height+hud_height), mode_options)
#screen = pygame.display.set_mode((width, height))
pygame.mouse.set_visible(False)


globalz = Globalz(num_players,
                  joystick_count, 
                  screen, 
                  width, height,
                  hud_height,
                  BG_COLOR,
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
    "F": "FutureFloor.png",
    "W": "FutureWall.png",
    "D": "ForcePlayerFloor.png",
    "d": "ForceBoxFloor.png",
}
for x, filenm in tile_filenm_map.items():
    globalz.images[x] = pygame.image.load(filenm)
    globalz.images[x] = globalz.images[x].convert_alpha()


def run_game(g, level_filenm, hud, level_section):
    pygame.display.flip()

    clock = pygame.time.Clock()

    tb = TileBoard(g, 40, 54, filenm=level_filenm)

    start = (tb.start[0], tb.start[1], 1)
    player = Player(start)

    tick = 30

    running = True
    restart = False
    g.surface.fill((0,0,0))

    lt = LevelTitle(tb.g)
    start_time = time.time()

    while running:
        g.surface.fill((0,0,0))

        hud.draw(level_section.section_name, tb.level_name)

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
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        restart = "next section"
                    else:
                        restart = "next"
                    running = False
                elif event.key == pygame.K_p:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        restart = "prev section"
                    else:
                        restart = "prev"
                    running = False
                status = player.keyboard_event(event, tb)
                if status == "killed":
                    restart = True
                    running = False
                elif status == "won":
                    restart = "won"
                    running = False

            #print "++", event

        tb.draw(player.tile_loc)

        #elapsed = time.time() - start_time
        #if elapsed < 2.5:
        #    lt.draw(tb.level_name)

        pygame.display.flip()
        clock.tick(tick)

        pygame.display.set_caption("FPS: %.2f" % (clock.get_fps(),))
    #   x_sound.play()

    msg = None
    if status == "killed":
        msg = ["You failed.", "", "Try again."]
        mm = BadModalMessage(tb.g)
    elif status == "won":
        msg = "Good job!"
        mm = GoodModalMessage(tb.g)
    if msg is not None:
        mm.draw(msg)

    return restart



def main():
    lm = LevelManager()
    level_section = lm.level_sections[0]
    level_filenm = level_section.level_filenms[0]

    mm = GoodModalMessage(globalz)
    mm.draw(level_section.start_message)

    hud = HUD(globalz)

    while 1:
        restart = run_game(globalz, level_filenm, hud, level_section)
        globalz.surface.fill((0,0,0))
        if restart == "won":
            level_section, level_filenm = lm.next()
            if level_filenm is None:
                #lt = LevelTitle(globalz)
                #lt.draw("               You won!                 ")
                #pygame.display.flip()
                #time.sleep(1.5)
                mm = GoodModalMessage(globalz)
                mm.draw(["", " You won! ", ""])
                print >>sys.stderr, "No more levels."
                break
        elif restart in ("next", "prev", "next section", "prev section"):
            if restart == "next":
                tlevel_section, tlevel_filenm = lm.next()
            elif restart == "prev":
                tlevel_section, tlevel_filenm = lm.prev()
            elif restart == "next section":
                tlevel_section, tlevel_filenm = lm.next_section()
            elif restart == "prev section":
                tlevel_section, tlevel_filenm = lm.prev_section()
            if tlevel_filenm is not None:
                level_section, level_filenm = tlevel_section, tlevel_filenm
        elif restart is False:
            break

    pygame.quit()



if __name__=="__main__":
    import cProfile
    import pstats
    cProfile.run("main()", "profile.data")
    p = pstats.Stats("profile.data")
#   p.strip_dirs().sort_stats('time').print_stats()
#   main() 


