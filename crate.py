import pygame


"""
Game
    Section
        Level
            SubLevel

    * the Game is a set of Sections
        * one Section is flagged as the starting Section
        * Sections are "linked" by GoalCells

    * a Section is a set of Levels
        * Levels

    * a Level is a set of SubLevels

    * Crates can move between SubLevels within a Level

    * Teleporters connect cells which are within SubLevels in the same Level

    * GoalCells start a new Level or new Section

    * Switches trigger events within a Level

    cut-scenes, 
        at start of Section
        at reaching GoalCell


SubLevels
Cutscenes
Teleporters
GoalCells


"""


class Location:
    def __init__(self, level, x, y, z):
        pass



class Crate:
    legal_crate_move_tiles = set((" ", "I","D"))

    def __init__(self, g, image_key, loc):
        pass

    def move_to(self, loc):
        pass



class CrateManager:
    """
    keeps track of where all the crates are

    moves crates around
    """

    def find(self, x, y, z):
        """
        returns Crate found at location or None
        """


