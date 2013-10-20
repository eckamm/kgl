"""
Are the level configs going to remain human-editable?
    Would be nice.

Need a level config validator.
    Too easy right now to break engine with bad level config.

Will editor allow editing multiple levels or one at a time?
    Multiple would be ideal since linking the levels together
    is an important activity.

The in-game movement between levels is independent of the editing
environments movement between levels.

    In the editor, the levels are simply tagged with a name and
    the user can next/pref/goto on that name.

    In-game links will have been made to move the player between 
    the levels.

Levels configs have attributes:
    * is_start: one level can be marked as the starting level 
    * name: friendly name of level

editor states / work-flow

    start [basedir]    
        (all valid .kgl files are loaded)

    show first level (alphabetically by name or is_first)

    level navigation: 
        n: next
        p: previous
        g: goto (modal input)

    Z-level:
        have a toggle for z=0 or z=1 input; not necessary if the
        mouse input can be unambiguous
    objects:
        list all the objects in columns on the right; 
        
    * select a block/object type for the cursor
    * click on the grid to place the block/object

Blocks/objects must know where they are allowed to be placed.

Draw light outline of squares where cubes from z=0 and z=1 meet.
Detect clicks within the outlines.  If the blocks are meant for
either z=0 or z=1 (but not both), then the user doesn't need to
pick the z value.

A level is a rectangular region.  Start out 8x8.  Have buttons
(-T+ -B+ -L+ -R+) to move the edges of the region.  Even better,
drag the corners of the outline grid to resize.

This is pretty straighforward so far for simply placing tiles.
What about connecting a goal tile to a start tile?
    1. alt-click the goal tile
    2. now in "goal/start definition mode"
    3. ESC escapes the mode
    4. navigate to the start tile; no other operations are allowed
    5. alt-click the start tile

What about connecting a pressure plate to an effect?
    1. alt-click the presure plate tile
    2. now in "pressure plate trigger definition mode"
    3. ESC escapes the mode
    4. navigate to the affected tile; no other operations are allowed
    5. alt-click the affected tile


Rendering strategy:
    * the board being rendered is rectangular
    * translate the top-left corner coord to 0,0
    * the tile art must include the front facing rect within 
      the image used to position sprite while rendering


"""
import sys
import os
import glob
import logging
import pygame

from buttons import Buttons
from level import Level


logger = logging.getLogger("leveleditor")



def mk_empty_start_level(g, filenm):
    level = Level(g, filenm)
    level.size = (8, 8)
    return level


def mk_color_set():
    colors = []
    for i in range(25):
        color = (i*2, i*2, i*2)
        colors.append(color)
    colors.extend(reversed(colors))
    return colors



class LevelEditor:
    def __init__(self, dirnm, event_manager):
        self.em = event_manager
        self.connections = [
        ]
        logger.info("LevelEditor being created")
        self.dirnm = dirnm
        self._levels = {}
        self._load_levels()

    def _load_level_file(self, filenm):
        self._levels[filenm] = Level(self.g, filenm)

    def _find_level_files(self):
        filenms = glob.glob(os.path.join(self.dirnm, "*.kgl"))
        return sorted(filenms)

    def _load_levels(self):
        filenms = self._find_level_files()
        for filenm in filenms:
            self._load_level_file(filenm)
        if not self._levels:
            # Create an empty initial level.
            filenm = os.path.join(self.dirnm, "000-start.kgl")
            level = mk_empty_start_level(self.g, filenm)
            self._levels[filenm] = level

            
    def run(self):
        g = self.g
        tick = 30
        clock = pygame.time.Clock()
        running = True

        level_key = sorted(self._levels.keys())[0]

        disp_w, disp_h = self.g.surface.get_size()

        board_surface = self.g.surface.subsurface(
            pygame.Rect((0,0), (disp_w/2, disp_h*7/8)))

        buttons_surface = self.g.surface.subsurface(
            pygame.Rect((0, disp_h*7/8), (disp_w, disp_h/8)))

        tao_surface = self.g.surface.subsurface(
            pygame.Rect((disp_w/2, 0), (disp_w/2, disp_h*7/8)))

        buttons = Buttons(self.g, buttons_surface)

        bg_colors = mk_color_set()
        frame_cnt = 0
        while running:

            if True: # debug
                # Pulse the background to see what's being redrawn.
                self.g.surface.fill(
                    bg_colors[frame_cnt%len(bg_colors)])

            if g.android:
                if g.android.check_pause():
                    g.android.wait_for_resume()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):

                    if buttons.collidepoint(event.pos):
                        action = buttons.mouse_event(event, buttons_surface)
                        if action is not None:
                            if action.lower() == "abort":
                                running = False
                            elif action == "+":
                                level.change_size(1)
                            elif action == "-":
                                level.change_size(-1)

                    if level.collidepoint(event.pos, board_surface):
                        action = level.mouse_event(event, board_surface)



            level = self._levels[level_key]
            level.draw(board_surface)

            buttons.draw()
     
            pygame.display.flip()
            frame_cnt += 1
            clock.tick(tick)

    def dump(self, fp=sys.stderr):
        print >>fp, "#levels: %s" % len(self._levels)
        for key, level in sorted(self._levels.items()):
            print >>fp, "Level: %s" % (key,)
            print >>fp, "    size: %s" % (level.size,)




