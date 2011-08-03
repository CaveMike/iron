#! /usr/bin/python
from iron.context import Context
from iron.dispatcher import Dispatcher
from iron.state import State
import logging
import sys
import unittest

class TestState(unittest.TestCase):
    class TestObj(object):
        STATE_STOPPED = 'Stopped'
        STATE_STARTED = 'Started'
        STATE_PAUSED  = 'Paused'

        def __init__( self ):
            self.log = logging.getLogger( self.__class__.__name__ )

            self.lastHandler = None
            self.state = State( self, self.STATE_STOPPED, { self.STATE_PAUSED : 30 } )

        def identifyState( self, event ):
            return self.state.identifyState( event )

        # Commands
        @Dispatcher.eventHandler
        def Start( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Dispatcher.eventHandler
        def Stop( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Dispatcher.eventHandler
        def Pause( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Stopped
        def inStopped_onStart( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )
            self.state.changeState( self.STATE_STARTED )

        def inStopped_onEnter( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStopped_onLeave( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStopped_onDefault( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Started
        def inStarted_onPause( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )
            self.state.changeState( self.STATE_PAUSED )

        def inStarted_onStop( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )
            self.state.changeState( self.STATE_STOPPED )

        def inStarted_onEnter( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStarted_onLeave( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStarted_onDefault( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Paused
        def inPaused_onStart( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )
            self.state.changeState( self.STATE_STARTED )

        def inPaused_onStop( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )
            self.state.changeState( self.STATE_STOPPED )

        def inPaused_onEnter( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inPaused_onLeave( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inPaused_onDefault( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Default
        def onEnter( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def onEnter( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def onDefault( self, event, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

    def runTest( self ):
        d = Dispatcher.getInstance()

        c = Context( 'Root' )
        c.start()

        o = self.TestObj()
        d.add( obj=o, parentObj=None, context=c )

        o.Start()
        assert( str(o.state.currentState) == o.STATE_STARTED )
        assert( str(o.lastHandler) == 'inStarted_onEnter' )
        o.Pause()
        assert( str(o.state.currentState) == 'Paused' )
        assert( str(o.lastHandler) == 'inPaused_onEnter' )
        o.Stop()
        assert( str(o.state.currentState) == 'Stopped' )
        assert( str(o.lastHandler) == 'inStopped_onEnter' )

        c.stop()

if __name__ == '__main__':
    logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()

