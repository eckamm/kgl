import weakref


class Event:
    def __init__(self):
        self.name = "Generic Event"


class EventManager:
    def __init__(self):
        self.listeners = weakref.WeakKeyDictionary

    def register_listener(self, listener):
        self.listeners[listener] = 1

    def unregister_listener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        for listener in self.listeners.keys():
            listener.Notify(event)



