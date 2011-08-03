#!/usr/bin/env python
from iron.dispatcher import Dispatcher
import logging

class StateEvent(object):
    """
    An event that can also specify state transitions using the newState and
    oldState member variables.
    """
    def __init__( self, id, newState, oldState = None ):
        super( StateEvent, self ).__init__()
        self.id = id
        self.newState = newState
        self.oldState = oldState

    def __call__( self ):
        return self.id

    def __str__( self ):
        return 'id: %s, newState: %s, oldState: %s' % ( str(self.id), str(self.newState), str(self.oldState) )

class State(object):
    EVENT_ENTER        = 'Enter'
    EVENT_LEAVE        = 'Leave'
    EVENT_TIMEOUT      = 'Timeout'
    EVENT_STATE_CHANGE = 'StateChange'

    """
    A state-machine based on a single state variable.
    Enforces optional state timeouts.
    Can generate internal leave, enter, and timeout events.
    """
    def __init__( self, obj, initialState, stateTimeouts = {} ):
        super( State, self ).__init__()
        self.log = logging.getLogger( self.__class__.__name__ )

        if not obj:
            raise TypeError( 'This state does not have an owner object.' )
        self.obj = obj

        if not initialState:
            raise TypeError( 'This state does not have an initial state.' )
        self.initialState = initialState

        self.currentState = None
        self.stateTimeouts = stateTimeouts
        self.stateTimer = None
        self.resetState()

    def resetState( self ):
        """
        Set the current state to the initial state.
        """
        if not self.initialState:
            raise TypeError( 'This state does not have an initial state.' )

        self.log.info( 'Resetting state to ' + str(self.initialState) + '.' )
        self.currentState = self.initialState
        self.stopStateTimer()

    def identifyState( self, event ):
        """
        Return the current state as the state variable.
        """

        return str(self.currentState)

    def changeState( self, newState, notify = False ):
        """
        Transition to the new state and optionally notify listeners.
        The state transition will also generate and process internal leave and enter events.
        """

        if self.currentState == None:
            raise Exception( 'This state does not have a current state.' )

        oldState = self.currentState

        # Only execute block if the state is really changing.
        if oldState != newState:
            # Stop state timer.
            self.stopStateTimer()

            # Leave pseudo-event.
            Dispatcher.getInstance().send( StateEvent( self.EVENT_LEAVE, newState = newState, oldState = oldState ), self.obj, self.obj )

            # Change state.
            self.log.info( 'Changing state from %s to %s.' % ( str(oldState), str(newState) ) )
            self.currentState = newState

            # Enter pseudo-event.
            Dispatcher.getInstance().send( StateEvent( self.EVENT_ENTER, newState = newState, oldState = oldState ), self.obj, self.obj )

            # Notify listeners.
            if notify:
                self.log.info( 'Notify listeners of the state change.' )
                Dispatcher.getInstance().notify( StateEvent( self.EVENT_STATE_CHANGE, newState = newState, oldState = oldState ), self.obj )

            # Start state timer.
            self.startStateTimer()

    def startStateTimer( self ):
        """
        If the current state is configured with a state timeout, then start the state timer.
        """

        stateTimeout = self.stateTimeouts.get( self.currentState, None )

        if stateTimeout:
            self.log.info( 'Start state timer with a timeout of ' + str(stateTimeout) + '.' )

            if self.stateTimer:
                self.stopStateTimer()

            self.stateTimer = Dispatcher.getInstance().schedule( stateTimeout, StateEvent( self.EVENT_TIMEOUT, newState = self.currentState ), self.obj, self.obj )

    def stopStateTimer( self ):
        """
        Stop the state timer if it is running.
        """

        if self.stateTimer:
            self.log.info( 'Stop state timer.' )

            self.stateTimer.cancel()
            self.stateTimer = None

    def __str__( self ):
        return 'state: %s, timer: %s, timeouts: %s' % ( str(self.currentState), str(self.stateTimer), str(self.stateTimeouts) )

