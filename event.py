#!/usr/bin/env python
class Event(object):
    """
    A simple, example event that can be used with Dispatcher.
    This class can also be used as a base class for other events.
    """
    def __init__( self, id ):
        super( Event, self ).__init__()
        self.id = id

    def __call__( self ):
        return self.id

    def __str__( self ):
        return str(self.id)
