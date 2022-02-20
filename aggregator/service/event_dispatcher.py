

class EventDispatcher:
    def __init__(self):
        self.__listeners = {}

    def add_listener(self, event_type, listener):
        if event_type not in self.__listeners:
            self.__listeners[event_type] = []
        self.__listeners[event_type].append(listener)

    def dispatch(self, event):
        if event.type in self.__listeners:
            for listener in self.__listeners[event.type]:
                listener(event)
