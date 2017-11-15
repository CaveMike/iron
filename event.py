#!/usr/bin/env python3
class Event:
    """
    A simple, example event that can be used with Dispatcher.
    This class can also be used as a base class for other events.
    """
    def __init__(self, name):
        super(Event, self).__init__()
        self.name = name

    def __call__(self):
        return self.name

    def __str__(self):
        return str(self.name)
