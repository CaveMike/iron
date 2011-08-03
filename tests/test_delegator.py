#! /usr/bin/python
from iron.delegator import Delegator
import logging
import sys
import unittest

class TestDelegator1(unittest.TestCase):
    class connection(object):
        STATE_DISCONNECTED = 'Disconnected'
        STATE_CONNECTED    = 'Connected'

        def __init__( self ):
            super( TestDelegator1.connection, self ).__init__()
            self.log = logging.getLogger( self.__class__.__name__ )
            self.state = self.STATE_DISCONNECTED
            self.lastHandler = None

        def identifyState( self, event ):
            return self.state

        @Delegator.eventHandler
        def Connect( self ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Disconnect( self ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inDisconnected_onConnect( self ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.state = self.STATE_CONNECTED

        def inConnected_onDisconnect( self ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.state = self.STATE_DISCONNECTED

    class TestObj(object):
        STATE_STOPPED = 'Stopped'
        STATE_STARTED = 'Started'
        STATE_PAUSED  = 'Paused'

        def __init__( self ):
            super( TestDelegator1.TestObj, self ).__init__()
            self.log = logging.getLogger( self.__class__.__name__ )
            self.state = self.STATE_STOPPED
            self.lastHandler = None
            self.connection = TestDelegator1.connection()

        @Delegator.eventHandler
        def Stop( self ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Start( self ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Pause( self, timeout = 0 ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Test( self, id, message ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Query( self, id ):
            self.log.debug( sys._getframe().f_code.co_name + ', ' + str(id) )

        @Delegator.eventHandler
        def Connect( self ):
            self.log.debug( sys._getframe().f_code.co_name + '' )

        @Delegator.eventHandler
        def Disconnect( self ):
            self.log.debug( sys._getframe().f_code.co_name + ', ' + str(id) )

        def identifyState( self, event ):
            return self.state

        # Stopped
        def inStopped_onStart( self ):
            self.state = self.STATE_STARTED
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStopped_onDefault( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + ', ' + str(args) + ', ' + str(kwargs) )

        # Started
        def inStarted_onPause( self, timeout ):
            self.state = self.STATE_PAUSED
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + ', timeout: ' + str(timeout) )

        def inStarted_onStop( self ):
            self.state = self.STATE_STOPPED
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStarted_onConnect( self ):
            self.connection.Connect()
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inStarted_onDisconnect( self ):
            self.connection.Disconnect()
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Paused
        def inPaused_onStart( self ):
            self.state = self.STATE_STARTED
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        def inPaused_onStop( self ):
            self.state = self.STATE_STOPPED
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + '' )

        # Default
        def onDefault( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + ', ' + str(args) + ', ' + str(kwargs) )

        # Default
        def onTest( self, *args, **kwargs ):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug( sys._getframe().f_code.co_name + ', ' + str(args) + ', ' + str(kwargs) )

    def runTest( self ):
        o = self.TestObj()

        o.Stop()
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inStopped_onDefault' )

        o.Pause()
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inStopped_onDefault' )

        o.Start()
        assert( str(o.state) == self.TestObj.STATE_STARTED )
        assert( str(o.lastHandler) == 'inStopped_onStart' )

        o.Connect()
        assert( str(o.state) == self.TestObj.STATE_STARTED )
        assert( str(o.lastHandler) == 'inStarted_onConnect' )
        assert( str(o.connection.state) == self.connection.STATE_CONNECTED )
        assert( str(o.connection.lastHandler) == 'inDisconnected_onConnect' )

        o.Disconnect()
        assert( str(o.state) == self.TestObj.STATE_STARTED )
        assert( str(o.lastHandler) == 'inStarted_onDisconnect' )
        assert( str(o.connection.state) == self.connection.STATE_DISCONNECTED )
        assert( str(o.connection.lastHandler) == 'inConnected_onDisconnect' )

        o.Stop()
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inStarted_onStop' )

        o.Start()
        assert( str(o.state) == self.TestObj.STATE_STARTED )
        assert( str(o.lastHandler) == 'inStopped_onStart' )

        o.Pause( 30 )
        assert( str(o.state) == self.TestObj.STATE_PAUSED )
        assert( str(o.lastHandler) == 'inStarted_onPause' )

        o.Test( 0, message = 'hi' )
        assert( str(o.state) == self.TestObj.STATE_PAUSED )
        assert( str(o.lastHandler) == 'onTest' )

        o.Query( 12 )
        assert( str(o.state) == self.TestObj.STATE_PAUSED )
        assert( str(o.lastHandler) == 'onDefault' )

        o.Start()
        assert( str(o.state) == self.TestObj.STATE_STARTED )
        assert( str(o.lastHandler) == 'inPaused_onStart' )

        o.Pause( 30 )
        assert( str(o.state) == self.TestObj.STATE_PAUSED )
        assert( str(o.lastHandler) == 'inStarted_onPause' )

        o.Stop()
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inPaused_onStop' )

        o.Test( 0, message = 'hi' )
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inStopped_onDefault' )

        o.Query( 12 )
        assert( str(o.state) == self.TestObj.STATE_STOPPED )
        assert( str(o.lastHandler) == 'inStopped_onDefault' )

if __name__ == '__main__':
    #logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    logging.basicConfig( level=logging.INFO, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()

