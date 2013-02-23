from events import *
import logging


LOGGER = logging.getLogger("editorstate")



class EditorState:
    def __init__(self, event_manager):
        self.em = event_manager
        self.connections = [
            self.em.register(TAOSelectionEvent, self.on_tao_selection),
            self.em.register(LevelKeyChangeEvent, self.on_level_key_changed),
#           self.em.register(TAOPlacementRequestEvent, self.on_tao_placement_request),
        ]
        self.current_tile_key = None
        self.current_tile = None
        self.current_level_key = None


    def on_tao_selection(self, event):
        self.current_tile_key = event.tile_key
        self.current_tile = event.tile


    def on_level_key_changed(self, event):
        self.current_level_key = event.level_key

#   def on_tao_placement_request(self, event):
#       event.tile_key
#       event.level_key
#       event.x
#       event.y


