import os
import sys
import json
import array
import pygame
from crate import Crate

"""
    "p": "Character.png",
        the player
            moves around
            can push crates
            can fall in holes
            is blocked by I=ForcePlayer

    "f": "WoodFloor.png",
    "g": "GrassFloor.png",
    "w": "WoodWall.png",
    "s": "StoneFloor.png",
        these "wall" tiles block all movement

    "G": "GoalTile.png",
        when player reaches any goal tile, the level is won

    "c": "Crate.png",
        player can push, but not into i=ForceBox or a "wall" tile

    "i": "ForceBox.png",
        only blocks movement of box

    "I": "ForcePlayer.png",
        only blocks movement of player

Read the static tiles in to a 1D array and establish max_x and max_y for indexing.
Put the non-static tiles in a dict of sets keyed by (x,y,z).

}"""


class TileBoard:

    bg_color = (0, 0, 0)

    def __init__(self, g, bx, by, filenm):
        self.g = g
        self.bx, self.by = bx, by

        self._load_data(filenm)

        self.grid_width = len(self.data[0][0])
        self.grid_height = len(self.data[0])

        self._init_constants()
        self._mk_tile_surfaces()
        self.make_bg()

    def _load_data(self, filenm):
        with open(filenm) as fp:
            jdat = json.load(fp)
            self.level_name = jdat["name"]
            self.data = jdat["level"]
#           self._mk_permdata()
            self.start = jdat["start"]
            self.jdat = jdat
        assert len(self.data[0]) == len(self.data[1])
        assert len(self.data[0][0]) == len(self.data[1][0])

        objects = {}
        data1d = array.array("c")  # array of chars
        object_keys = ("c",)
        for tz, layer in enumerate(self.data):
            for ty, row in enumerate(layer):
                for tx, cell in enumerate(row):
                    if cell in object_keys:
                        loc = (tx, ty, tz)
                        objects.setdefault(loc, set()).add(cell)
                    if cell in object_keys:
                        cell = " " 
                    data1d.append(str(cell))
        self.data1d = data1d
        self.objects = objects


    def _old_mk_tile_surfaces(self):
        """
        scale the global tile images for use in this TileBoard
        """
        self.tiles = {}
        if getattr(self.g, "images", None) is None:
            print >>sys.stderr, "WARNING: no tile images available"
            return
        for k in self.g.images:
            if len(k) != 1:
                continue
            if k == "p":
                sz = (self.player_width, self.player_height)
            else:
                sz = (self.tile_width, self.tile_height+self.layer_offset)
            self.tiles[k] = pygame.transform.scale(self.g.images[k], sz)

    def _mk_tile_surfaces(self):
        """
        scale the global tile images for use in this TileBoard
        """
        self.tiles = {}

        for tile_key, tile in self.g.tm.tiles.items():
            if tile_key == "p":
                sz = (self.player_width, self.player_height)
            else:
                sz = (self.tile_width, self.tile_height+self.layer_offset)
            self.tiles[tile_key] = pygame.transform.scale(tile.img_surf, sz)

    def _init_constants(self):
        w, h = self.g.width, self.g.height
        if self.grid_width >= self.grid_height:
            self.tile_width = (w - self.bx * 2) // self.grid_width
            self.tile_height = self.tile_width
            self.fit_type = "width"
            self.xshift = 0
            self.yshift = -self.by + (self.g.height-self.tile_height*self.grid_height) // 2
        else:
            self.tile_height = (h - self.by * 2) // self.grid_height
            self.tile_width = self.tile_height
            self.fit_type = "height"
            self.xshift = -self.bx + (self.g.width-self.tile_width*self.grid_width) // 2
            self.yshift = 0
        self.layer_offset = int(self.tile_height // 2)
        self.player_width = int(self.tile_width // 2)
        self.player_height = int((self.tile_height * 4) // 3)
	self.player_offset = -int(self.player_height // 3)

    def dump_constants(self):
        print >>sys.stderr, "w=%s h=%s hud=%s" % (self.g.width, self.g.height, self.g.hud_height)
        print >>sys.stderr, "fit_type=%s" % (self.fit_type)
        print >>sys.stderr, "gw=%s gh=%s" % (self.grid_width, self.grid_height)
        print >>sys.stderr, "tw=%s th=%s" % (self.tile_width, self.tile_height)
        print >>sys.stderr, "lo=%s" % self.layer_offset
        print >>sys.stderr, "pw=%s ph=%s" % (self.player_width, self.player_height)
        print >>sys.stderr, "po=%s" % self.player_offset


    def xform_coord(self, tx, ty, tz):
        x = self.xshift + self.bx + tx * self.tile_width
        y = self.yshift + self.by + ty * self.tile_height - tz * self.layer_offset
        return x, y
        
    def make_bg(self):
        w = (2+self.grid_width) * self.tile_width
        h = (2+self.grid_height) * self.tile_height
        self._bg = pygame.surface.Surface((w, h))
        self._bg.fill(self.bg_color)

#   def draw_bg(self):
#       self.g.surface.blit(self._bg, (self.bx-self.tile_width, self.by-self.tile_height))

    def old_draw(self, ploc):
#       self.draw_bg()
        for tz, layer in enumerate(self.data):
            for ty, row in enumerate(layer):
                for tx, cell in enumerate(row):
                    x, y = self.xform_coord(tx, ty, tz)
                    # Draw the player first.
                    if (tx, ty, tz) == ploc:
                        tile = self.tiles.get("p")
                        px = x + self.tile_width // 4
			py = y + self.player_offset
                        self.g.surface.blit(tile, (px, y))
                    # Draw the (transparent) tile over the player.
                    tile = self.tiles.get(cell)
                    if tile is not None:
                        self.g.surface.blit(tile, (x, y))
                    cell2 = self.get_cell_perm((tx,ty,tz))
                    if cell2 in ("I",)and cell!=cell2:
                        tile = self.tiles.get(cell2)
                        self.g.surface.blit(tile, (x,y))

    def draw(self, ploc):
        
        EMPTY_TILE_KEYS = " ."

        for tz in range(2):
            for ty in range(self.grid_height):
                for tx in range(self.grid_width):
                    x, y = self.xform_coord(tx, ty, tz)
                    i = tz*(self.grid_width*self.grid_height) + ty*self.grid_width + tx
                    tile_key = self.data1d[i]
                    if tile_key in EMPTY_TILE_KEYS:
                        tile = None
                    else:
                        tile = self.tiles.get(tile_key)
                    # Draw the tile.
                    if tile is not None:
                        self.g.surface.blit(tile, (x, y))
                    # Draw the objects.
                    for object_key in self.objects.get((tx, ty, tz), ()):
                        tile = self.tiles.get(object_key)
                        if tile is not None:
                            self.g.surface.blit(tile, (x, y))
                    # Draw the player.
                    if (tx, ty, tz) == ploc:
                        tile = self.tiles.get("p")
                        px = x + self.tile_width // 4
			py = y + self.player_offset
                        self.g.surface.blit(tile, (px, y))


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

    def set_cell(self, loc, cell_key):
        x, y, z = loc
        idx = z*(self.grid_width*self.grid_height) + y*self.grid_width + x
        self.data1d[idx] = cell_key


    def move_cell(self, src, dest):
        cell, ig = self.get_cell(src)
        self.set_cell(src, " ")
        self.set_cell(dest, cell)
        # Drop in hole if hole is underneath.
        hole_loc = (dest[0], dest[1], dest[2]-1)
        if self.get_cell(hole_loc)[0] in Crate.legal_crate_move_tiles:
            self.move_cell(dest, hole_loc)

    def move_object(self, object_key, src, dest):
        """
        move an object (1-byte string) from src to dest
        
        *Does not* if move is legal.
        *Does* drop crates into holes.
        """
        # Remove the object from its old location.
        self.objects[src].remove(object_key)
        # Also remove the objects dict entry if the src location is now empty.
        if not self.objects[src]:
            del self.objects[src]
        # Add the object to its new location.
        self.objects.setdefault(dest, set()).add(object_key)
        # Drop crate if hole is underneath.
        if object_key == "c" and dest[2]==1:
            hole_loc = (dest[0], dest[1], dest[2]-1)
            cell, objects = self.get_cell(hole_loc)
            if cell in Crate.legal_crate_move_tiles and len(objects-Crate.legal_crate_move_tiles)==0:
                self.move_object(object_key, dest, hole_loc)
    
    def dump(self):
        print self.data1d
        print self.objects

        for tz in range(2):
            for ty in range(self.grid_height):
                for tx in range(self.grid_width):
                    i = tz*(self.grid_width*self.grid_height) + ty*self.grid_width + tx
                    sys.stdout.write(self.data1d[i])
                print
            print

        for tz in range(2):
            for ty in range(self.grid_height):
                for tx in range(self.grid_width):
                    i = tz*(self.grid_width*self.grid_height) + ty*self.grid_width + tx
                    print ("[%3s %s]" % (i, self.data1d[i])).ljust(7),
                print
            print


if __name__=="__main__":
    class G:
        pass
    g = G()
    g.width = 640
    g.height = 640
    g.hud_height = 50
    bx, by = (40, 40)
    filenm = "levels/set-10/level_1.kgl"
    tb = TileBoard(g, bx, by, filenm, )
    tb.dump()
    tb.dump_constants()


