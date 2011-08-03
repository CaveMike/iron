#! /usr/bin/python
from iron.event import Event
from iron.context import Context
import copy
import time
import unittest

class TestObj():
    def __init__( self, events ):
        self.events = copy.copy( events )

    def process( self, event, *args, **kwargs ):
        expected = self.events.pop(0)
        assert expected == event
        return 'Processed ' + event()

class TestContextThreaded(unittest.TestCase):
    def runTest( self ):
        events = [ Event( 'event0' ), Event( 'event1' ), Event( 'event2' ) ]

        o = TestObj( events )

        c = Context( 'context0' )
        c.start()

        for event in events:
            future = c.queue( event, o, o )
            #print future
            #future.cancel()
            #print future()
            #print future
        time.sleep( 0.1 )

        c.stop()

class TestContextPolled(unittest.TestCase):
    def runTest( self ):
        events = [ Event( 'event0' ), Event( 'event1' ), Event( 'event2' ) ]

        o = TestObj( events )

        c = Context( 'context0' )

        for event in events:
            future = c.queue( event, o, o )
        time.sleep( 0.1 )

        c.poll()

if __name__ == '__main__':
    logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()
