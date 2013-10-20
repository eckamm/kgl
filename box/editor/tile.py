"""


                 Wall Tile

      y_size = 7  +-----+  0
                  |     |  1
                  |     |  2 Floor Tile
                  |     |  3
    y_anchor = 6  +-----+  4  +-----+   y_size = 5
                  |     |  5  |     |
                  A-----+  6  A-----+   y_anchor = 2
                              |     |
                              +-----+

          offset = (0, 7)     offset = (0, )

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


A current wall tile is 64x96.  The "top" is 64x64 and the "wall" is 64x32.

The scaling of a tile should be done for the width.  The height and y-offset
need to be scaled proportionally the same.

  

          A = (25, 66)
    tile_sz = (41, 41)
     img_sz = (64, 96)  ->  (41, 61.5)


"""
import pygame
import sys
import logging
import glob
import os
import json

LOGGER = logging.getLogger("tile")


class TileLoadError(Exception):
    pass


class TileManager:
    def __init__(self, dirnm):
        self.tiles = self._load_tiles(dirnm)

    def _load_tiles(self, dirnm):
        tiles = {}
        pattern = os.path.join(dirnm, "*.json")
        filenms = glob.glob(pattern)
        for filenm in filenms:
            try:
                tile = Tile(filenm)
                LOGGER.info("loaded %r" % (filenm,))
            except TileLoadError, msg:
                LOGGER.info("ignoring %r; %s" % (filenm, msg))
                continue
            if tile.key in tiles.keys():
                LOGGER.info("ignoring %r; duplicate tile key %r" % (filenm, tile.key))
                continue
            tiles[tile.key] = tile
        return tiles

    def calc_consts(self, tile_sz):
        """
        call this whenever the resolution of the grid changes
        """
        for tile in self.tiles.itervalues():
            tile.calc_consts(tile_sz)
        


class Tile:
    def __init__(self, filenm):
        self.json_filenm = filenm
        self.img_filenm = os.path.splitext(filenm)[0] + ".png"
        # load the png image
        if not os.path.exists(self.img_filenm):
            raise TileLoadError("no image file")
        self.img_surf = pygame.image.load(self.img_filenm)
        # load the json metadata
        fp = open(self.json_filenm)
        self.jdat = json.load(fp)
        fp.close()
        # treat some of the attributes formally
        self.key = self.jdat.get("key")
        if self.key is None:
            raise TileLoadError("missing attribute 'key'")
        self.img_offset = self.jdat.get("offset")
        if self.img_offset is None:
            # This default will work for full width wall tiles.
            self.img_offset = (0, self.img_surf.get_height()-1)

    def calc_consts(self, tile_sz):
        """
        given the board's tile size, calculate the constants
        which are needed to scale the tile image
        """
        w,h = self.img_surf.get_size() # image size
        self._nw = tile_sz[0]          # desired image width
        r = self._nw / float(w)        # scaling factor
        self._nh = int(h * r)          # scale image height

        ox, oy = self.img_offset       # image anchor offset in image coords
        self._nox = int(ox * r)        # scale anchor offset to screen coords
        self._noy = int(oy * r)        # scale anchor offset to screen coords

        LOGGER.debug("_nw=%s _nh=%s _nox=%s _noy=%s" % (self._nw, self._nh, self._nox, self._noy))


    def render(self, dest_surf, pos, tile_sz):
        self.calc_consts(tile_sz)

        LOGGER.debug("pos=%r tile_sz=%r" % (pos, tile_sz))
        src_surf = self.img_surf # need to scale surf

#       w,h = src_surf.get_size()  # image size
#       nw = tile_sz[0]            # desired image width
#       r = nw / float(w)          # scaling factor
#       nh = int(h * r)            # scale image height
        src_surf = pygame.transform.scale(src_surf, (self._nw, self._nh))  # scale image

        ox, oy = self.img_offset # image anchor offset in image coords
#       nox = int(ox * r)        # scale anchor offset to screen coords
#       noy = int(oy * r)        # scale anchor offset to screen coords

        tpos = (pos[0]+self._nox, pos[1]-self._noy)  # translate surf blit pos by anchor offset
        dest_surf.blit(src_surf, tpos)   # now blit

#       print >>sys.stderr, ("INFO: ox=%s oy=%s " % (ox, oy))

#       print >>sys.stderr, ("INFO: tpos=%r " % (tpos,))



