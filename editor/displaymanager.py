import logging

from events import *

import pygame

try:
    import android
except ImportError:
    android = None



LOGGER = logging.getLogger("displaymanager")


if android:
    LOGGER.info("found android")
else:
    LOGGER.info("no android")



class DisplayManager:
    def __init__(self, event_manager):
        self.em = event_manager
        self.connections = [
            self.em.register(SysInitRequiredEvent, self.on_sysinit_required),
        ]
        self.screen = None

    def on_sysinit_required(self, ev):
        # Do all the initialization related to the display.
        pygame.display.init()
        pygame.font.init()

        # Pick the screen size.
        if android:
            if False: # native
                screen = pygame.display.set_mode((0, 0))
                w, h = screen.get_size()
            else: # 1/4 native
                screen = pygame.display.set_mode((0, 0))
                w, h = screen.get_size()
                print "Native resolution:", (w, h)
                w = w / 2
                h = h / 2
                print "Set resolution:", (w, h)
                screen = pygame.display.set_mode((w, h))
                print "2:Set resolution:", screen.get_size()
        elif 1:
            info = pygame.display.Info()
            w, h = info.current_w, info.current_h
            h = int(4*h/5)
            w = int(4*w/5)
            screen = pygame.display.set_mode((w, h))
        else:
            #w, h = 540, 960  # HTC Vivid
            #w, h = 400, 400  # HTC Vivid
            #screen = pygame.display.set_mode((w, h))
            #screen = pygame.display.set_mode((540, 960), pygame.FULLSCREEN)
            #pygame.mouse.set_visible(False)
            #screen = pygame.display.set_mode((0, 0))
            #w, h = screen.get_size()
            #h = int(2*h/3)
            #w = int(2*w/3)
            #screen = pygame.display.set_mode((w, h))
            info = pygame.display.Info()
            w, h = info.current_w, info.current_h
            h = int(1*h/3)
            w = int(1*w/3)
            screen = pygame.display.set_mode((w, h))
        self.screen = screen

        LOGGER.info("size=%s bitsize=%s bytesize=%s" % (
            screen.get_size(), screen.get_bitsize(), screen.get_bytesize()))

        self.em.post(SysInitCompleteEvent())




