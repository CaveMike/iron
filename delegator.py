#!/usr/bin/env python
import logging
import types

class Delegator(object):
    """
    An object that processes events by finding and calling an appropriate event handler.
    """

    """
    Constants that define the naming conventions of event handlers.
    Set a format to None to disable a particular event handler.
    """
    STATE_HANDLER_FORMAT         = 'in{1}_on{0}'
    DEFAULT_STATE_HANDLER_FORMAT = 'in{1}_onDefault'
    EVENT_HANDLER_FORMAT         = 'on{0}'
    DEFAULT_EVENT_HANDLER_FORMAT = 'onDefault'

    """
    Pre-defined function names that are used to refine an event or state name.
    """
    FUNCTION_ID_EVENT  = 'identifyEvent'
    FUNCTION_ID_STATE  = 'identifyState'

    #
    log = logging.getLogger( 'Delegator' )

    @staticmethod
    def eventHandler( func ):
        """
        A decorator that can be used to redirect a standard method
        call to the internal event processing.

        For example:
            @Delegator.eventHandler
            def greenButtonPushed( self, *args, **kwargs ):
                print 'Green button pushed.'

        Will be changed to:
            def greenButtonPushed( self, *args, **kwargs ):
                print 'Green button pushed.'
                Delegator.log.debug( 'Process event, ' + 'greenButtonPushed.' )
                function = Delegator.getHandler( self, 'greenButtonPushed' )
                if function:
                    Delegator.log.info( 'Dispatching event, greenButtonPushed, to function, ' + str(function.__name__) + '.' )
                    return function( *args, **kwargs )
                else:
                    Delegator.log.debug( 'Unhandled event, greenButtonPushed.' )
        """
        def process( self, *args, **kwargs ):
            func( self, *args, **kwargs )
            Delegator.log.debug( 'Process event, ' + func.__name__ + '.' )
            function = Delegator.getHandler( self, func.__name__ )
            if function:
                Delegator.log.info( 'Dispatching event, ' + func.__name__ + ', to function, ' + str(function.__name__) + '.' )
                return function( *args, **kwargs )
            else:
                Delegator.log.debug( 'Unhandled event, ' + func.__name__ + '.' )
        return process

    @staticmethod
    def hasHandler( obj, event ):
        return Delegator.getHandler( obj, event ) != None

    @staticmethod
    def getHandler( obj, event ):
        event = Delegator.__identifyEvent( obj, event )
        if not event:
            Delegator.log.info( 'Ignoring event, ' + str(event) + '.' )
            return None

        if type(event) != types.StringType:
            event = event()

        function = None

        state = Delegator.__identifyState( obj, event )
        if state is not None:
            function = Delegator.findStateHandler( obj, event, state )

        if not function:
            function = Delegator.findEventHandler( obj, event )

        return function

    @staticmethod
    def findStateHandler( obj, event, state, allowDefaults = True ):
        """
        Find the best-fitting state event handler and return it.
        Otherwise return None.
        """

        function = None

        # Look for state event-handlers.
        if Delegator.STATE_HANDLER_FORMAT:
            Delegator.log.debug( 'State processing of ' + str(event) + ' in ' + str(state) + '.' )
            function = Delegator.findExactHandler( obj, Delegator.STATE_HANDLER_FORMAT.format(event, state) )

        # Look for the default state event-handler.
        if not function and Delegator.DEFAULT_STATE_HANDLER_FORMAT and allowDefaults:
            Delegator.log.debug( 'Default state processing of ' + str(event) + ' in ' + str(state) + '.' )
            function = Delegator.findExactHandler( obj, Delegator.DEFAULT_STATE_HANDLER_FORMAT.format(event, state) )

        return function

    @staticmethod
    def findEventHandler( obj, event, allowDefaults = True ):
        """
        Find the best-fitting event handler and return it.
        Otherwise return None.
        """

        function = None

        # Look for event handers.
        if Delegator.EVENT_HANDLER_FORMAT:
            Delegator.log.debug( 'Find handler for event, ' + str(event) + '.' )
            function = Delegator.findExactHandler( obj, Delegator.EVENT_HANDLER_FORMAT.format(event) )

        # Look for the default event-handler.
        if not function and Delegator.DEFAULT_EVENT_HANDLER_FORMAT and allowDefaults:
            Delegator.log.debug( 'Find default handler for event, ' + str(event) + '.' )
            function = Delegator.findExactHandler( obj, Delegator.DEFAULT_EVENT_HANDLER_FORMAT.format(event) )

        return function

    @staticmethod
    def findExactHandler( obj, functionName ):
        """
        Attempt to find an exact event-handler.
        If an event-handler is available, return it; otherwise return None.
        """
        Delegator.log.debug( 'Look for function, ' + str(functionName) + '.' )

        if hasattr( obj, functionName ):
            return getattr( obj, functionName )
        else:
            Delegator.log.debug( 'Failed to find function, ' + str(functionName) + '.' )
            return None

    @staticmethod
    def __identifyEvent( obj, event ):
        # Identify the event id based on the object implements identifyEvent().
        if hasattr( obj, Delegator.FUNCTION_ID_EVENT ):
            function = getattr( obj, Delegator.FUNCTION_ID_EVENT )
            if function:
                return function( event )

        return event

    @staticmethod
    def __identifyState( obj, event ):
        # Identify the current state if the object implements identifyState().
        if hasattr( obj, Delegator.FUNCTION_ID_STATE ):
            function = getattr( obj, Delegator.FUNCTION_ID_STATE )
            if function:
                return function( event )

        return None

