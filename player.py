import pygame

from crate import Crate




class Player:
    legal_player_move_tiles = set((" ", "i","d"))
    goal_tiles = ("G",)

    def __init__(self, tile_loc):
        self.tile_loc = tile_loc   # e.g. (1, 1, 1)

    def player_move(self, new_player_loc):
        self.tile_loc = new_player_loc

    def crate_move(self, new_player_loc, new_crate_loc, tb):
        cell, objects = tb.get_cell(new_crate_loc)
        if cell not in Crate.legal_crate_move_tiles or len(objects - Crate.legal_crate_move_tiles)>0:
            # Crate destination is illegal.
            return
        # Move the crate.
        tb.move_object("c", new_player_loc, new_crate_loc)
        # Move the player to its new location
        self.tile_loc = new_player_loc


    def keyboard_event(self, event, tb):
        if event.key == pygame.K_EQUALS:
            tb.dump_constants()
            tb.dump()

        new_player_loc = move_loc(event.key, self.tile_loc)
        if new_player_loc is None:
            # No move was input.
            return
        cell, objects = tb.get_cell(new_player_loc)
        #cell2 = tb.get_cell_perm(new_player_loc)
        if cell is None:
            # Player tried to move off board.
            return
        #if cell in self.legal_player_move_tiles and cell2 in self.legal_player_move_tiles: # and cell2 not in (_)
#       print ("+++", cell, objects, self.legal_player_move_tiles)
#       print cell in self.legal_player_move_tiles 
#       print (objects - self.legal_player_move_tiles)
        if cell in self.legal_player_move_tiles and len(objects - self.legal_player_move_tiles)==0:
            print "normal move"
            # Make a normal player move.
            self.player_move(new_player_loc)
        elif "c" in objects: # and (objects - self.legal_player_move_tiles):
            print "crate push"
            # Attempt a crate push move.
            new_crate_loc = move_loc(event.key, new_player_loc)
            self.crate_move(new_player_loc, new_crate_loc, tb)

        # Check if player is standing on solid ground. 
        t = (new_player_loc[0], new_player_loc[1], new_player_loc[2]-1)
        cell, objects = tb.get_cell(t)
        status = None
        if cell in self.legal_player_move_tiles and len(objects-self.legal_player_move_tiles)==0:
            status = "killed"
        elif cell in self.goal_tiles:
            status = "won"
        return status


def move_loc(key, loc):
    t = loc
    if key == pygame.K_UP:
        new_loc = (t[0], t[1]-1, t[2])
    elif key == pygame.K_DOWN:
        new_loc = (t[0], t[1]+1, t[2])
    elif key == pygame.K_LEFT:
        new_loc = (t[0]-1, t[1], t[2])
    elif key == pygame.K_RIGHT:
        new_loc = (t[0]+1, t[1], t[2])
    else:
        new_loc = None
    return new_loc
