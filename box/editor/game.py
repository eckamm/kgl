import pygame



class Game:
    STATE_SETUP = "setting up"
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_CLOSING = "closing down"

    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.state = Game.STATE_SETUP

    def notify(self, event):
        if isinstance(event, event_manager.TickEvent):
            if self.state == Game.STATE_SETUP:
                self.start()

    def start(self):
        self.state = Game.STATE_RUNNING
        # do setup stuff ??
        ev = event_manager.EditorStartedEvent(self)
        self.event_manager.post(ev)

