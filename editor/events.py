from eventsystem import Event


    
class GodhandEvent(Event):
    def __init__(self):
        self.name = "Godhand Event"


class TAOPlacementRequestEvent(Event):
    def __init__(self, x, y):
        self.name = "Tile and Object Placement Request Event"
        self.x = x
        self.y = y
#class TAOPlacementRequestEvent(Event):
#    def __init__(self, tile_key, level_key):
#        self.name = "Tile and Object Placement Request Event"
#        self.tile_key = tile_key
#        self.level_key = level_key

class TAOSelectionEvent(Event):
    def __init__(self, tile_key, tile):
        self.name = "Tile and Object Selection Event"
        self.tile_key = tile_key
        self.tile = tile


class CycleVisibilityEvent(Event):
    def __init__(self):
        self.name = "Cycle Visibility Event"


class EditorSaveEvent(Event):
    def __init__(self):
        self.name = "EditorSaveEvent"


class SysInitRequiredEvent(Event):
    def __init__(self):
        self.name = "System Initialization Required Event"


class DisplayResizeEvent(Event):
    """
    This event causes the views to adjust.
    """
    def __init__(self):
        self.name = "Display Resize Event"



class LevelKeyChangeRequestEvent(Event):
    """
    A request has been made to change the current Level.
    """
    def __init__(self, delta=0, index=0):
        self.name = "Level Key Change Request Event"
        self.delta = delta
        self.index = index


class LevelKeyChangeEvent(Event):
    """
    This event happens when you switch from one Level to another.
    """
    def __init__(self, level_key):
        self.name = "Level Key Change Event"
        self.level_key = level_key


class LevelManagerAddLevelRequestEvent(Event):
    def __init__(self):
        self.name = "Level Manager Add Level Request Event"


class LevelSizeChangeEvent(Event):
    """
    This event happens when the current Level.size changes
    """
    def __init__(self):
        self.name = "Level Key Change Event"



class SysInitCompleteEvent(Event):
    def __init__(self):
        self.name = "System Initialization Complete Event"


class TickEvent(Event):
    def __init__(self):
        self.name = "CPU Tick Event"


class LogLevelChangeEvent(Event):
    def __init__(self, delta):
        self.name = "Log Level Change Event"
        self.delta = delta


class QuitEvent(Event):
    def __init__(self):
        self.name = "Quit Event"


class SaveEvent(Event):
    def __init__(self):
        self.name = "Save Event"


class SaveQuitEvent(Event):
    def __init__(self):
        self.name = "Save Quit Event"


class ResizeLevelRequestEvent(Event):
    def __init__(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right


class LevelManagerDumpEvent(Event):
    def __init__(self):
        self.name = "LevelManager Dump Event"


########################################################################
########################################################################

# Some events are simply wrapped Pygame event.

class MouseButtonUpEvent(Event):
    def __init__(self, pg_event):
        self.name = "Pygame MOUSEBUTTONUP Event"
        self.pg_event = pg_event

