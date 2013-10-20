import weakref
import logging


LOGGER = logging.getLogger("eventsystem")


class Event:
    """
    base class for events used with the EventManager
    """



class EventManager:
    """
    Posting an Event which has no listeners will cause a KeyError.  This
    is OK since a completely disregarded Event is a bug.
    """
    def __init__(self):
        # self._listeners[key] -> [listener, ...]
        self._listeners = {}

    def register(self, eventClass, listener):
        """
        register a listener for eventClass type events

        The caller of EventManager.register must store the Connection 
        which is returned in a list attribute in order for the listener to 
        be automatically removed from the EventManager when that caller 
        is deleted.
        """
        LOGGER.debug("register %s" % eventClass.__name__)
        key = eventClass.__name__

        if (hasattr(listener, '__self__') and
            hasattr(listener, '__func__')):
            # Wrap the callable if it is an instance method.
            listener = EventManager.WeakBoundMethod(listener)

        self._listeners.setdefault(key, []).append(listener)

        LOGGER.debug("register count %s" % len(self._listeners[key]))
        return EventManager.Connection(self, eventClass, listener)

    def _remove(self, eventClass, listener):
        # This should only be invoked by Connection.__del__.
        # Maybe it should be moved there.
        key = eventClass.__name__
        self._listeners[key].remove(listener)

    def post(self, event):
        eventClass = event.__class__
        key = eventClass.__name__
        LOGGER.debug("post event %s (keys %s)" % (
            key, len(self._listeners[key])))
        for listener in self._listeners[key]:
            listener(event)

    class WeakBoundMethod:
        def __init__(self, meth):
            self._self = weakref.ref(meth.__self__)
            self._func = meth.__func__

        def __call__(self, *args, **kwargs):
            self._func(self._self(), *args, **kwargs)

    class Connection:
        """
        The EventManager returns a Connection when listener is added to 
        the EventManager.
        
        This Connection should be added to a list attribute on the object 
        which added the listener.

        If a reference to the Connection is not kept somewhere, the 
        Connection will be garbage collected and the listener binding 
        automatically disappears (see Connection.__del__).

        When a Connection is deleted, the side effect is that the weakref 
        in the EventManager will be cleaned up automatically.

        This frees the object which registers the listeners from needing 
        to remove the listeners explicitly before it is deleted.

        """
        def __init__(self, em, ec, lstnr):
            self.em = em
            self.ec = ec
            self.lstnr = lstnr

        def __del__(self):
            self.em._remove(self.ec, self.lstnr)
            LOGGER.debug("removed %s %s from %s" % (self.ec, self.lstnr, self.em))



def test():

    class QuitEvent(Event):
        pass

    class RunController:
        def __init__(self, event_mgr):
            # Must keep a reference to Connection or the listener
            # connection will disappear right away!
            self._connections = [event_mgr.register(QuitEvent, self.exit)]
            self.running = True
            self.event_mgr = event_mgr

        def exit(self, event):
            print "exit called"
            self.running = False

        def run(self):
            print "run called"
            while self.running:
                event = QuitEvent()
                self.event_mgr.post(event)
                LOGGER.debug(str(self.event_mgr._listeners))

    logging.basicConfig(level=logging.DEBUG)
    em = EventManager()
    run = RunController(em)
    print "--1"
    run.run()
    print "--2"
    print (QuitEvent, run.exit)
    print em._listeners
    #em._remove(QuitEvent, run.exit)
    print "--3"
    del run
    print em._listeners


if __name__=="__main__":
    test()
