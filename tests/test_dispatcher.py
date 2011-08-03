#! /usr/bin/python
from iron.event import Event
from iron.dispatcher import Dispatcher
from iron.context import Context
from threading import Timer
import logging
import sys
import unittest

class TestDispatcher(unittest.TestCase):
    class TestObj(object):
        def __init__( self ):
            self.log = logging.getLogger( self.__class__.__name__ )
            self.lastHandler = None

        def on1( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def on2( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def on4( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def onDefault( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

    def runTest( self ):
        c = Context( 'Root' )
        c.start()

        o0 = self.TestObj()
        Dispatcher.add( obj=o0, parentObj=None, context=c )

        o1 = self.TestObj()
        Dispatcher.add( obj=o1, parentObj=None, context=c )
        Dispatcher.addListener( srcObj=o1, dstObj=o0 )

        Dispatcher.send( event=Event( '1' ), srcObj=o0, dstObj=o1 )
        assert( str(o1.lastHandler) == 'on1' )

        Dispatcher.queue( event=Event( '2' ), srcObj=o0, dstObj=o1 )
        #assert( str(o1.lastHandler) == 'on2' )

        Dispatcher.send( event=Event( '3' ), srcObj=o0, dstObj=o1 )
        #assert( str(o1.lastHandler) == 'on3' )

        Dispatcher.notify( event=Event( '4' ), srcObj=o1 )
        #assert( str(o1.lastHandler) == 'on4' )
        Dispatcher.notify( event=Event( '4' ), srcObj=o1 )
        #assert( str(o1.lastHandler) == 'on4' )

        c.stop()

if __name__ == '__main__':
    logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()

