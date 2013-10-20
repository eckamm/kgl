import sys
import logging

from init import init
from displaymanager import DisplayManager
from levelmanager import LevelManager
from leveleditor import LevelEditor
from tile import TileManager
from editorstate import EditorState
from pygameview import PygameView

from eventsystem import EventManager
from events import *

import pygame

LOGGER = logging.getLogger("main")



FPS = 30



class CPUSpinnerController:
    def __init__(self, event_manager):
        self.em = event_manager
        self.connections = [
            self.em.register(QuitEvent, self.on_quit),
            self.em.register(SysInitCompleteEvent, self.on_sysinit_complete),
        ]
        self.is_running = True
        self.clock = pygame.time.Clock()

    def on_sysinit_complete(self, ev):

        self.em.post(DisplayResizeEvent())

        # This is the main loop for the game.
        while self.is_running:
            # Limit the framerate.
            self.clock.tick(FPS)
            # Advance the game.
            self.em.post(TickEvent())

    def on_quit(self, ev):
        # Stop the main loop.
        self.is_running = False



class InputController:
    def __init__(self, event_manager):  
        self.em = event_manager
        self.connections = [
            self.em.register(TickEvent, self.on_tick),
        ]

    def on_tick(self, ev):
        # Handle the Pygame events by creating the appropriate game events.
        for pg_event in pygame.event.get():

            if pg_event.type == pygame.QUIT:
                self.em.post(QuitEvent())

            elif pg_event.type == pygame.KEYDOWN: 
                if pg_event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.em.post(QuitEvent())

                elif pg_event.key == pygame.K_l:
                    if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        self.em.post(LogLevelChangeEvent(1))
                    else:
                        self.em.post(LogLevelChangeEvent(-1))

                elif pg_event.key == pygame.K_d:
                    self.em.post(LevelManagerDumpEvent())

                elif pg_event.key == pygame.K_EQUALS:
                    self.em.post(ResizeLevelRequestEvent(0, 0, 1, 1))
                    LOGGER.info("BIGGER")

                elif pg_event.key == pygame.K_MINUS:
                    self.em.post(ResizeLevelRequestEvent(0, 0, -1, -1))
                    LOGGER.info("SMALLER")

                elif pg_event.key == pygame.K_g:
                    self.em.post(GodhandEvent())
                    LOGGER.info("GODHAND")

                elif pg_event.key == pygame.K_v:
                    self.em.post(CycleVisibilityEvent())


            elif pg_event.type == pygame.MOUSEBUTTONUP:
                self.em.post(MouseButtonUpEvent(pg_event))




def on_log_level_change(event):
    """
    change the log level on all the 
    """
    logger_names = [
        "root", "buttons", "displaymanager", "eventsystem",
        "level", "leveleditor", "levelmanager", "main",
        "pygameview", "tile",
    ]
    log_levels = [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR]
    for nm in logger_names:
        logger = logging.getLogger(nm)
        print nm, logger.getEffectiveLevel()
        i = log_levels.index(logger.getEffectiveLevel())
        i = (i+event.delta) % len(log_levels)
        logger.setLevel(log_levels[i])



def setup_logging():
    log_format = "%(name)s:%(levelname)s:%(asctime)s %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(format=log_format, datefmt=date_format, level=logging.INFO)
#   logging.getLogger("eventsystem").setLevel(logging.DEBUG)



def main(dirnm):
    setup_logging()
    logging.info("test")

    em = EventManager()
    connections = [
        em.register(LogLevelChangeEvent, on_log_level_change)
    ]

    editor_state = EditorState(em)

    spinner = CPUSpinnerController(em)
    input_controller = InputController(em)

    display_manager = DisplayManager(em)

    tile_manager = TileManager("../images")

    level_manager = LevelManager(dirnm, editor_state, em)

    pygame_view = PygameView(em, 
                             display_manager, 
                             tile_manager,
                             level_manager)

#   em.post(DisplayResizeEvent())

    em.post(SysInitRequiredEvent())
    # the spinner will start running after the sysinit is complete

    
#   g = init()
#   level_editor.run()
#   level_editor.dump()


if __name__=="__main__":

    if len(sys.argv) == 2:
        level_set_dirnm = sys.argv[1]
    else:
        level_set_dirnm = "levels/level-set-001"

    main(level_set_dirnm)


