"""

    +-------+--+
    |       |  |    A: Level
    |   A   |B |    B: TilesAndObjects
    |       |  |    C: Buttons
    +-------+--+
    |     C    |
    +----------+

    * P: previous level
    * N: next level
    * +: new level
    * S: save levels
    * Q: quit without saving

    +----------+
    | P N +    |
    +----------+

"""
import logging
import pygame

from events import *


LOGGER = logging.getLogger("buttons")


def mk_button_surf(font, text, border_size):
    # Get the text render surface size.
    fw, fh = font.size(text)
    # Add the border size to the size.
    w, h = (fw+2*border_size, fh+2*border_size)
    # Create a background box surface.
    box_surf = pygame.Surface((w, h))
    box_surf.fill((40, 40, 40))
    # Render the text surface.
    text_surf = font.render(text, True, (200, 200, 100))
    # Blit the text surface onto the box surface.
    box_surf.blit(text_surf, (border_size, border_size))
    return box_surf


class Button:
    """
    * btn_surf holds the button image
    * subsurf is a child surface which is used to:
        A. anchor the position of the rendering
        B. do point collision detection
    Rather than using a subsurf, Button could have parent and pos attributes.
    """
    border_size = 5

    def __init__(self, font, text, parent_surf, topleft):
        self.text = text
        self.btn_surf = mk_button_surf(font, text, self.border_size)
        # By subsurface-ing the parent_surf and holding onto that new subsurface,
        # it is not possible to blit that subsurface onto the parent due to surface locks.
        self.subsurf = parent_surf.subsurface(topleft, self.btn_surf.get_size())
        self.subsurf.blit(self.btn_surf, (0, 0))

    def draw(self):
        self.subsurf.get_parent().blit(self.btn_surf, self.subsurf.get_offset())

    def collidepoint(self, pos):
        # pos is in absolute coords such as you might get from a mouse event.
        # Translate self's rect to absolute coords.
        abs_rect = self.subsurf.get_rect(topleft=self.subsurf.get_abs_offset())
        return abs_rect.collidepoint(pos)

    @classmethod
    def calc_size(cls, font, text):
        w, h = font.size(text)
        return (w+2*cls.border_size, h+2*cls.border_size)

    def mouse_event(self, event, surf):
        """
        look for a mouse-button-up on button regions

        return the "command" name of the button
        """
        ox, oy = self.surf.get_abs_offset()
        mx, my = event.pos 
        mx += ox
        my += oy

        #if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        if event.type == pygame.MOUSEBUTTONUP:
            for btn in self.buttons:
                print btn.text

        print surf.get_rect(), event.pos

    def __repr__(self):
        return "<Button: %s>" % (self.text,)



class Buttons:
    commands = (
        "+",
        "-",
        "prev",
        "next",
        "add",
        "save",
        "save/quit",
        "abort",
    )

    def __init__(self, subsurf, event_manager):
        LOGGER.info("Buttons.subsurf.size=%r" % (subsurf.get_size(),))
        self.em = event_manager
        self.connections = [
            self.em.register(MouseButtonUpEvent, self.on_mouse_button_up),
        ]
        pygame.font.init() # may already have been done
        font_size = subsurf.get_size()[1] // 3
        self.font = pygame.font.Font("freesansbold.ttf", font_size)
        self.subsurf = subsurf

        self.calc_rects()

        self.buttons = []
        for text, rect in zip(self.commands, self.rects):
            btn = Button(self.font, text, self.subsurf, rect.topleft)
            self.buttons.append(btn)

    def calc_rects(self):
        # Get the sizes of the buttons.
        sizes = []
        for cmd in self.commands:
            sizes.append(Button.calc_size(self.font, cmd))
        # Get the total width of the buttons.
        self.buttons_w = sum([size[0] for size in sizes])
        # Get the max height of the buttons.
        self.buttons_h = max([size[1] for size in sizes])
        # Calc the padding and spacing for the buttons.
        surf_w, surf_h = self.subsurf.get_size()
        self.pad_w = surf_w / 15
        self.pad_h = surf_h / 4
        self.space_w = (surf_w - self.buttons_w - 2 * self.pad_w) / (len(self.commands)-1)
        # Calc the rects for the buttons.
        self.rects = []
        y = self.pad_h
        x = self.pad_w
        for size in sizes:
            self.rects.append(pygame.Rect((x, y), size))
            x += size[0] + self.space_w

    def collidepoint(self, pos):
        # pos is in absolute coords such as you might get from a mouse event.
        # Translate self's rect to absolute coords.
        abs_rect = self.subsurf.get_rect(topleft=self.subsurf.get_abs_offset())
        return abs_rect.collidepoint(pos)

    def draw(self):
        for btn in self.buttons:
            btn.draw()

    def on_mouse_button_up(self, event):
        """
        look for a mouse-button-up on button regions

        return the "command" name of the button
        """
        retval = None
        if self.collidepoint(event.pg_event.pos):
            for btn in self.buttons:
                if btn.collidepoint(event.pg_event.pos):
                    LOGGER.info("mouse button up in %r" % btn)
                    retval = btn.text
                else:
                    pass
                    #print "no:", btn.text

        # React to the button press.
        if retval == "+":
            self.em.post(ResizeLevelRequestEvent(0, 0, 1, 1))
        elif retval == "-":
            self.em.post(ResizeLevelRequestEvent(0, 0, -1, -1))
        elif retval == "abort":
            self.em.post(QuitEvent())
        elif retval == "next":
            self.em.post(LevelKeyChangeRequestEvent(delta=1))
        elif retval == "prev":
            self.em.post(LevelKeyChangeRequestEvent(delta=-1))
        elif retval == "add":
            self.em.post(LevelManagerAddLevelRequestEvent())
        elif retval == "save":
            self.em.post(EditorSaveEvent())
        elif retval == "save/quit":
            self.em.post(EditorSaveEvent())
            self.em.post(QuitEvent())

        return retval
        #print surf.get_rect(), event.pos

"""
given the Buttons+Button objects and surf
    establish the set of Button rects

This needs to happen whenever the position of Buttons changes
or the Button objects inside Buttons changes.

Is this like a GUI "pack" function.

"""


