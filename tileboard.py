import os
import sys
import json
import pygame
from copy import deepcopy


class TileBoard:
    legal_crate_move_tiles = (" ","I")


    bg_color = (0, 0, 0)

    tile_width = 20
    tile_height = 20
    layer_offset = tile_height // 2

    player_width = tile_width // 2
    player_height = (tile_height * 4) // 3

    def _init_constants(self):
        w, h = self.g.width, self.g.height
        self.tile_width = (w - self.bx * 2) // self.grid_width
        self.tile_height = self.tile_width

    def __init__(self, g, bx, by, filenm=None):
        self.g = g
        self.bx, self.by = bx, by

        if filenm is None:
            self._mk_default_data()
        else:
            self._load_data(filenm)

        self.grid_width = len(self.data[0][0])
        self.grid_height = len(self.data[0])

        #self._init_constants()

        self.tiles = {}
        for k in self.g.images:
            if len(k) != 1:
                continue
            if k == "p":
                sz = (self.player_width, self.player_height)
            else:
                sz = (self.tile_width, self.tile_height+self.layer_offset)
            self.tiles[k] = pygame.transform.scale(self.g.images[k], sz)

        self.make_bg()

    def _load_data(self, filenm):
        with open(filenm) as fp:
            jdat = json.load(fp)
            self.level_name = jdat["name"]
            self.data = jdat["level"]
            self.permdata = deepcopy(self.data)
            self.start = jdat["start"]

    
    def _mk_default_data(self):
        self.data = [
            [
            "gggggggggggggggggg",
            "gggggggggggggggggg",
            "gffffffffffffffffg",
            "gf ffffffffffffffg",
            "gffffffffffffffffg",
            "gffffffffffffffffg",
            "gffffffffffffffffg",
            "gffffffffffffffffg",
            "gffffffffffffffffg",
            "gggggggggggggggggg",
            "gggggggggggggggggg",
            ],
            [
            "                  ",
            "                  ",
            " ssssssssssss sss ",
            " s       x      s ",
            " s       x      s ",
            " s       x      s ",
            " s              s ",
            " s              s ",
            " sss ssssssssssss ",
            "                  ",
            "                  ",
            ],
        ][:2]



    def xform_coord(self, tx, ty, tz):
        x = self.bx + tx * self.tile_width
        y = self.by + ty * self.tile_height - tz * self.layer_offset
        return x, y
        
    def make_bg(self):
        self
        w = (2+self.grid_width) * self.tile_width
        h = (2+self.grid_height) * self.tile_height
        self._bg = pygame.surface.Surface((w, h))
        self._bg.fill(self.bg_color)

    def draw_bg(self):
        self.g.surface.blit(self._bg, (self.bx-self.tile_width, self.by-self.tile_height))

    def draw(self, ploc):
        self.draw_bg()
        for tz, layer in enumerate(self.data):
            for ty, row in enumerate(layer):
                for tx, cell in enumerate(row):
                    x, y = self.xform_coord(tx, ty, tz)
                    # Draw the player first.
                    if (tx, ty, tz) == ploc:
                        tile = self.tiles.get("p")
                        px = x + self.tile_width // 4
                        self.g.surface.blit(tile, (px, y))
                    # Draw the (transparent) tile over the player.
                    tile = self.tiles.get(cell)
                    if tile is not None:
                        self.g.surface.blit(tile, (x, y))
                    cell2 = self.get_cell_perm((tx,ty,tz))
                    if cell2 in ("I",)and cell!=cell2:
                        tile = self.tiles.get(cell2)
                        self.g.surface.blit(tile, (x,y))

    def get_cell(self, loc):
        x, y, z = loc
        if x < 0 or y < 0 or z < 0 or z > 1:
            return None
        if x >= self.grid_width or y >= self.grid_height:
            return None
        return self.data[loc[2]][loc[1]][loc[0]]

    def get_cell_perm(self, loc):
        x, y, z = loc
        if x < 0 or y < 0 or z < 0 or z > 1:
            return None
        if x >= self.grid_width or y >= self.grid_height:
            return None
        return self.permdata[loc[2]][loc[1]][loc[0]]

    def move_cell(self, src, dest):
        cell = self.get_cell(src)
        self.set_cell(src, " ")
        self.set_cell(dest, cell)
        # Drop in hole if hole is underneath.
        hole_loc = (dest[0], dest[1], dest[2]-1)
        if self.get_cell(hole_loc) in self.legal_crate_move_tiles:
            self.move_cell(dest, hole_loc)

    def set_cell(self, loc, ncell):
        data = []
        for tz, layer in enumerate(self.data):
            data.append([]) # start a layer
            for ty, row in enumerate(layer):
                data[-1].append([]) # start a row
                for tx, cell in enumerate(row):
                    if (tx, ty, tz) == loc:
                        cell = ncell
                    data[-1][-1].append(cell) # add each column
                data[-1][-1] = "".join(data[-1][-1]) # stringify
        self.data = data
    

