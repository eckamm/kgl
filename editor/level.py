"""
One class will represent a Level.

Another class will represent a BoardScreen which is a Level being drawn on the display.

A Level is peristed to a disk file.  It can be loaded, edited, and saved.

A BoardScreen is used to render a loaded Level to the display.


"start" is a special object and goes into its own key



"""
import os
import logging
import array
import random
import json

import pygame

from events import *
from data1d import Data1D


LOGGER = logging.getLogger("level")


DEFAULT_LEVEL_SIZE = (8, 8)




class Level:
    """
    em
    lm
    objects
    size
    data1d
    """
    def __init__(self, filenm, level_manager, event_manager):
        self.em = event_manager
        self.lm = level_manager
        self.connections = [
            self.em.register(ResizeLevelRequestEvent, self.on_resize_level_request),
            self.em.register(GodhandEvent, self.on_godhand),
            self.em.register(EditorSaveEvent, self.on_editor_save),
        ]

        self.filenm = filenm
        if not os.path.exists(self.filenm):
            # Make an empty default level if the file is missing.
            self._mk_default()
        else:
            # Otherwise, load the level from the file.
            self._load()


    def _mk_default(self):
        self.size = DEFAULT_LEVEL_SIZE
        self.data1d = array.array("c", [" "]*self.size[0]*self.size[1]*2)
        self.objects = {} # objects[(x,y,z)] -> list of dicts
        self.tiles = {}

    def xform_coord(self, tx, ty, tz):
        x = self.xshift + self.bx + tx * self.tile_width
        y = self.yshift + self.by + ty * self.tile_height - tz * self.layer_offset
        return x, y


    def get_cell(self, loc):
        x, y, z = loc
        idx = z*(self.grid_width*self.grid_height) + y*self.grid_width + x
        if 0 <= idx < len(self.data1d):
           try:
            return self.data1d[idx], self.objects.get(loc, set())
           except:
            raise
            import pdb; pdb.set_trace()
        else:
            return None, set()

#   def set_cell(self, loc, cell_key):
#       x, y, z = loc
#       idx = z*(self.grid_width*self.grid_height) + y*self.grid_width + x
#       self.data1d[idx] = cell_key

    def set_cell(self, loc, tao_key):
        x, y, z = loc
        idx = z*(self.size[0]*self.size[1]) + y*self.size[0] + x
        print type(tao_key)
        self.data1d[idx] = tao_key.encode('ascii')


    def on_resize_level_request(self, event):
        if self != self.lm.current_level:
            # FIX: this should use EditorState, no lm.current_level
            return

        # FINISH: need to add check for whether deleted area is empty

        empty_chars = " "

        shape = (self.size[0], self.size[1], 2)
        d1d = Data1D(shape, self.data1d)

        start_size = self.size

        fillchar = " "
        min = 2
        max = 32

        if event.left > 0 and d1d.shape[0] < max-1:
            d1d.change_size("left", "add", fillchar)
        if event.left < 0 and d1d.shape[0] > min and d1d.is_empty("column", 0):
            d1d.change_size("left", "delete")
        if event.right > 0 and d1d.shape[0] < max-1:
            d1d.change_size("right", "add", fillchar)
        if event.right < 0 and d1d.shape[0] > min and d1d.is_empty("column", d1d.shape[0]-1):
            d1d.change_size("right", "delete")
        if event.top > 0 and d1d.shape[1] < max-1:
            d1d.change_size("top", "add", fillchar)
        if event.top < 0 and d1d.shape[1] > min and d1d.is_empty("row", 0):
            d1d.change_size("top", "delete")
        if event.bottom > 0 and d1d.shape[1] < max-1:
            d1d.change_size("bottom", "add", fillchar)
        if event.bottom < 0 and d1d.shape[1] > min and d1d.is_empty("row", d1d.shape[1]-1):
            d1d.change_size("bottom", "delete")

        self.size = d1d.shape[:2]
        self.data1d = array.array("c", d1d.data1d)

        if self.size != start_size:
            self.em.post(LevelSizeChangeEvent())
            LOGGER.info("new size=%r for %r" % (self.size, self))

        # FINISH: Also need to consider whether there are any objects
        # defined in the areas being deleted. 

    def on_godhand(self, event):
        """
        randomly add a tile to the board
        """
        z0_keys = "sgG"
        z1_keys = "wW"
        tile_key = random.choice(z0_keys+z1_keys)
        tx = random.randrange(self.size[0])
        ty = random.randrange(self.size[1])
        if tile_key in z0_keys:
            tz = 0
        else:            
            tz = 1
        LOGGER.info("on_godhand: %s: %s,%s,%s" % (tile_key, tx, ty, tz))
        idx = tz*(self.size[0]*self.size[1]) + ty*self.size[0] + tx
        self.data1d[idx] = tile_key

    def __repr__(self):
        return "<Level: %r>" % (self.filenm,)


    def on_editor_save(self, event):
        """
        writes out a .kgl formatted level file
            name: "level name"
            start: [0, 0]
            level: [["ff", "ff"], ["ww", "ww]]
        """
        # Put the level attributes in a JSON friendly data structure.
        jdat = {
            "name": getattr(self, "name", "level name"),
            "start": getattr(self, "start", [0, 0]),
        }
        jdat["level"] = []
        for z in range(2):
            jdat["level"].append([])
            for y in range(self.size[1]):
                row = []
                for x in range(self.size[0]):
                    idx = x + y*self.size[0] + z*self.size[0]*self.size[1]
                    cell = self.data1d[idx]
                    row.append(cell)
                jdat["level"][-1].append("".join(row))
        # Dump the JSON to disk.
        fp_out = open(self.filenm, "w")
        json.dump(jdat, fp_out, indent=4)
        fp_out.close()


    def _load(self):
        LOGGER.info("load level from file: %r" % (self.filenm,))
        fp = open(self.filenm)
        jdat = json.load(fp)
        fp.close()
        self.name = jdat["name"]
        self.start = jdat["start"]
        self.data1d = []
 #      import pdb; pdb.set_trace()
        for z in range(len(jdat["level"])):
            for y in range(len(jdat["level"][z])):
                for x in range(len(jdat["level"][z][y])):
                    self.data1d.append(str(jdat["level"][z][y][x]))
        self.data1d = array.array("c", "".join(self.data1d))
        self.size = [
            len(jdat["level"][0][0]),
            len(jdat["level"][0]),
        ]


'''
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

    def draw_tiles(self, surf, start_x, start_y, tile_w, tile_h):

        t1 = self.g.tile_manager.tiles["w"]
        t2 = self.g.tile_manager.tiles["s"]
        t3 = self.g.tile_manager.tiles["g"]
        t4 = self.g.tile_manager.tiles["G"]

        grid_w, grid_h = self.size

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

    def draw(self, surf):
        logger.info("draw level %r" % (self.filenm,))

        grid_w, grid_h = self.size
        surf_w, surf_h = surf.get_size()
        pad_w = (surf_w/15)
        pad_h = (surf_h/15)
        tile_w = (surf_w - pad_w*2) / grid_w
        tile_h = (surf_h - pad_h*2) / grid_h
        #tile_h = tile_h * 2 / 3

        self.draw_edit_grid(surf, pad_w, pad_h, tile_w, tile_h)
        self.draw_tiles(surf, pad_w, pad_h, tile_w, tile_h)


    def collidepoint(self, pos, subsurf):
        # pos is in absolute coords such as you might get from a mouse event.
        # Translate self's rect to absolute coords.
        abs_rect = subsurf.get_rect(topleft=subsurf.get_abs_offset())
        return abs_rect.collidepoint(pos)
'''



def mk_empty_start_level(g, filenm):
    level = Level(g, filenm)
    level.size = (8, 8)
    return level


