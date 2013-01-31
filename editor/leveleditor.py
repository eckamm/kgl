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


logger = logging.getLogger("leveleditor")


DEFAULT_LEVEL_SIZE = (8, 8)


class TileSprite:
    """
                     Wall Tile

          y_size = 7  +-----+  0
                      |     |  1
        y_anchor = 6  +-----+  2 Floor Tile
                      |     |  3
                      |     |  4  +-----+   y_size = 5
                      |     |  5  |     |
                      A-----+  6  A-----+   y_anchor = 2
                                  |     |
                                  +-----+

    Point "A" is logically anchored to the bottom-left of each
    cell in the board's grid during rendering.

    The x and y offset of A within the image file in terms of 
    pixels must be known for each sprite.  This is the a 2-tuple.
    called the image_anchor_offset.

    +--+--+--+  This is the z=0 grid for a 3x3 level.
    |  |  |  |
    A--B--C--+  If a tile is at (1,1) its image_anchor would be rendered at E.
    |  |  |  |
    D--E--F--+
    |  |  |  |
    G--H--I--+

    The grid will be drawn onto a surface dedicated to the board.
    There needs to be some padding to accommodate the height of 
    tiles.

    +-------+--+
    |       |  |    A: Level
    |   A   |B |    B: TilesAndObjects
    |       |  |    C: Buttons
    +-------+--+
    |     C    |
    +----------+

    """
    def __init__(self, image):
        pass       


class Level:
    def __init__(self, g, filenm=None):
        self.g = g
        self.filenm = filenm
        if not os.path.exists(self.filenm):
            # Make an empty default level if the file is missing.
            self._mk_default()
        else:
            # Otherwise, load the level from the file.
            self._load()

    def _mk_default(self):
        self.size = DEFAULT_LEVEL_SIZE
        self.objects = {}
        self.tiles = {}

    def _load(self):
        logger.info("load level from file: %r" % (self.filenm,))

    def change_size(self, delta):
        self.size = (self.size[0]+delta, self.size[1]+delta)

    def draw_edit_grid(self, surf, start_x, start_y, tile_w, tile_h):
        color = (200, 200, 200)
        grid_w, grid_h = self.size

        end_y = start_y + grid_h*tile_h
        for i in xrange(grid_w+1):
            x = start_x + i * tile_w
            pygame.draw.line(surf, color, (x, start_y), (x, end_y))

        end_x = start_x + grid_w*tile_w
        for i in xrange(grid_h+1):
            y = start_y + i * tile_h
            pygame.draw.line(surf, color, (start_x, y), (end_x, y))


    def draw(self, surf):
        logger.info("draw level %r" % (self.filenm,))

        grid_w, grid_h = self.size
        surf_w, surf_h = surf.get_size()
        pad_w = (surf_w/15)
        pad_h = (surf_h/15)
        tile_w = (surf_w - pad_w*2) / grid_w
        tile_h = (surf_h - pad_h*2) / grid_h

        self.draw_edit_grid(surf, pad_w, pad_h, tile_w, tile_h)




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
    def __init__(self, g, dirnm):
        self.g = g
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
                            
                        print "+++", action

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




