"""
This is where all the logic related to drawing the graphics happens.

The PygameView picks the sizes of the display regions based on the
DisplayManager.screen dimensions.

How should the Buttons region and individual buttons work?
Do buttons have separate view and model classes?  Not really.

The Buttons class should EventManager.register on_mouse_button_up



"""
import logging

from events import *
from buttons import Buttons
from tao import TAO

import pygame



LOGGER = logging.getLogger("pygameview")

INVISIBLE_KEYS = " ."


class BoardView:
    def __init__(self, 
                 board_surface, 
                 level_manager, 
                 tile_manager, 
                 event_manager):
        self.em = event_manager
        self.lm = level_manager
        self.tm = tile_manager
        self.board_surface = board_surface
        self.visibility = 0 # 0->z=both 1->z=0 2->z=1
        self.connections = [
            self.em.register(CycleVisibilityEvent, self.on_cycle_visibility),
            self.em.register(MouseButtonUpEvent, self.on_mouse_button_up),
#           self.em.register(DisplayResizeEvent, self.on_display_resize),
#           self.em.register(TickEvent, self.on_tick),
        ]
#   def on_display_resize(self, event):
        # These constants are used for drawing on the board_surface.
        grid_w, grid_h = self.lm.current_level.size
        surf_w, surf_h = self.board_surface.get_size()
        self.pad_w = (surf_w/15)
        self.pad_h = (surf_h/15)
        self.tile_w = (surf_w - self.pad_w*2) / grid_w
        self.tile_h = (surf_h - self.pad_h*2) / grid_h

        self.ctrl = []


    def on_cycle_visibility(self, event):
        self.visibility = (self.visibility + 1) % 3


    def draw_edit_grid(self):
        start_x = self.pad_w
        start_y = self.pad_h
        tile_w = self.tile_w
        tile_h = self.tile_h

        lvl = self.lm._levels[self.lm.current_key]
        grid_size = lvl.size

        surf = self.board_surface

        color = (30, 30, 30)
        grid_w, grid_h = grid_size

        end_y = start_y + grid_h*tile_h
        for i in xrange(grid_w+1):
            x = start_x + i * tile_w
            pygame.draw.line(surf, color, (x, start_y), (x, end_y))

        end_x = start_x + grid_w*tile_w
        for i in xrange(grid_h+1):
            y = start_y + i * tile_h
            pygame.draw.line(surf, color, (start_x, y), (end_x, y))

        ctrl = []
        surf = self.board_surface
        r = surf.get_rect()
        for i in xrange(grid_w):
            for j in xrange(grid_h):
                x = start_x + i * tile_w
                y = start_y + j * tile_h
                r = pygame.Rect(x, y, tile_w, tile_h)
                ctrl.append((r, i, j))
        self.ctrl = ctrl


    def on_mouse_button_up(self, event):
        """
        look for a mouse-button-up on button regions

        Posts a TAOSelectionEvent if a tile or object was selected.
        """
        surf = self.board_surface
        surf_abs_rect = surf.get_rect(topleft=surf.get_abs_offset())
        if surf_abs_rect.collidepoint(event.pg_event.pos):
            if not self.ctrl:
                # no tiles shown in select area yet
                return
            for rect, gx, gy in self.ctrl:
                # rect is in local coords to start with
                r = rect.copy()
                r.move_ip(surf_abs_rect.left, surf_abs_rect.top)
                if r.collidepoint(event.pg_event.pos):
                    LOGGER.info("mouse button up in %r" % ((gx, gy),))
                    self.em.post(TAOPlacementRequestEvent(gx, gy))


    def xform_coord(self, tx, ty, tz):
       #x = self.xshift + self.bx + tx * self.tile_width
       #y = self.yshift + self.by + ty * self.tile_height - tz * self.layer_offset
        x = self.pad_w + tx * self.tile_w
        y = self.pad_h + (ty+1) * self.tile_h
        return x, y


    def draw(self):
        start_x = self.pad_w
        start_y = self.pad_h + self.tile_h
        tile_w = self.tile_w
        tile_h = self.tile_h
        surf = self.board_surface

        grid_w, grid_h = self.lm.current_level.size
        data1d = self.lm.current_level.data1d
        tm_get = self.tm.tiles.get

#       data1d[0] = "w"
#       data1d[10] = "w"
#       data1d[12] = "G"
#       data1d[13] = "g"
#       data1d[14] = "s"
#       data1d[15] = "w"
#       data1d[30] = "w"

        for tz in [0, 1]:
            # 0->z=both 1->z=0 2->z=1
            if self.visibility == 0:
                pass
            elif self.visibility == 1 and tz==0:
                continue
            elif self.visibility == 2 and tz==1:
                continue

            for ty in range(grid_h):
                for tx in range(grid_w):
                    i = tz*(grid_w*grid_h) + ty*grid_w+ tx
                    tile_key = data1d[i]
                    tile = tm_get(tile_key)
                    # Draw the tile.
                    if tile is not None and tile_key not in INVISIBLE_KEYS:
                        #x, y = self.xform_coord(tx, ty, tz, tile.img_offset[1])
                        x, y = self.xform_coord(tx, ty, tz)
                        #surf.blit(tile.img_surf, (x, y))
                        tile.render(surf, (x, y), (tile_w, tile_h))


                #   # Draw the objects.
                #   for object_key in self.objects.get((tx, ty, tz), ()):
                #       tile = self.tiles.get(object_key)
                #       if tile is not None:
                #           self.g.surface.blit(tile, (x, y))
                    # Draw the player.
                #   if (tx, ty, tz) == ploc:
                #       tile = self.tiles.get("p")
                #       px = x + self.tile_width // 4
                #       py = y + self.player_offset
                #       self.g.surface.blit(tile, (px, y))



        return
        start_y = start_y + tile_h
        for j in xrange(grid_h):
            for i in xrange(grid_w):
                x = start_x + i*tile_w
                y = start_y + j*tile_h
                t = None
                if (i,j) in ((0,0),):
                    t = t1
                elif (i,j) in ((1,1), (2,1)):
                    t = t3
                elif (i,j) in ((4,4),(4,5)):
                    t = t2
                elif (i,j) in ((grid_w-1, grid_h-1),):
                    t = t4
                if t:
#                   import pdb; pdb.set_trace()
                    pygame.draw.circle(surf, (100,250,250), (x,y), 2)
                    # think top down for block_sz
                    block_sz = (tile_w, tile_h) 
                    t.render(surf, (x,y), block_sz)
                #t1.render(t.surf, (x,y), (tile_w, tile_h))
                #surf.blit(t.surf, (x,y))





class PygameView:
    def __init__(self, event_manager, 
                       display_manager,
                       tile_manager,
                       level_manager):
        self.em = event_manager
        self.connections = [
            self.em.register(DisplayResizeEvent, self.on_display_resize),
            self.em.register(LevelKeyChangeEvent, self.on_display_resize),
            self.em.register(LevelSizeChangeEvent, self.on_display_resize),
            self.em.register(TickEvent, self.on_tick),
        ]
        self.dm = display_manager
        self.tm = tile_manager
        self.lm = level_manager

        self.board_surface = None
        self.board_view = None

        self.buttons_surface = None
        self.tao_surface = None

        self.buttons = None
        self.tao = None



    def on_display_resize(self, event):
        """
        * also used when switching Levels
        * also used when changing a Level's grid size
        """
        disp_surf = self.dm.screen
        disp_w, disp_h = disp_surf.get_size()

        # The board is where the current level is shown
        # in the top left.
        self.board_surface = disp_surf.subsurface(
            pygame.Rect((0,0), (disp_w/2, disp_h*7/8)))
        self.board_view = BoardView(self.board_surface, self.lm, self.tm, self.em)

        # "buttons" is the collection of buttons across the bottom.
        self.buttons_surface = disp_surf.subsurface(
            pygame.Rect((0, disp_h*7/8), (disp_w, disp_h/8)))
        self.buttons = Buttons(self.buttons_surface, self.em)
        self.buttons.calc_rects()

        # "tao" means "tiles and objects"
        # It's the selection control for tiles and objects
        # in the top right.
        self.tao_surface = disp_surf.subsurface(
            pygame.Rect((disp_w/2, 0), (disp_w/2, disp_h*7/8)))
        self.tao = TAO(self.tao_surface, self.tm, self.em)


    def on_tick(self, event):
        #LOGGER.info("[[render]]")

        screen = self.dm.screen

        screen.fill((0, 0, 0))

        tm = self.tm

        self.board_view.draw_edit_grid()
        self.board_view.draw()

        self.buttons.draw()
        self.tao.draw()

        pygame.display.update()



"""
There should be a LevelView used in conjunction with the
    * LevelManager.current_level (a Level)
    * and the board_surface
"""

