import pygame

try:
    import android
except ImportError:
    android = None

try:
    import pygame.mixer as mixer
    mixer.init()
except ImportError:
    import android.mixer as mixer

import os


class Globals:
    pass


def init():
    g = Globals()

    g.android = android
    g.mixer = mixer

    # On Android map the back button to the escape key.
    if android:
        android.init()
        android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
        android.map_key(android.KEYCODE_BACK, pygame.K_q)

    pygame.display.init()
    pygame.font.init()

    # Set the screen size.
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
        h = int(2*h/5)
        w = int(2*w/5)
        screen = pygame.display.set_mode((w, h))


    print "w=%s h=%s" % (w,h)
    print "***", screen.get_size(), screen.get_bitsize(), screen.get_bytesize()
    width, height = w, h
    hud_height = h / 10
 
    g.surface = screen
    g.width = width
    g.height = height-hud_height
    g.hud_height = hud_height

    return g


