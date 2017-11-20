#!/usr/bin/env python3
import logging
from typing import Dict
from dispatcher import Dispatcher

class StateEvent:
    """
    An event that can also specify state transitions using the new_state and
    old_state member variables.
    """
    def __init__(self, id: str, new_state: str, old_state: str=None) -> None:
        super(StateEvent, self).__init__()
        self.id = id
        self.new_state = new_state
        self.old_state = old_state

    def __call__(self) -> str:
        return self.id

    def __str__(self):
        return 'id: %s, new_state: %s, old_state: %s' % (str(self.id), str(self.new_state), str(self.old_state))

class State:
    EVENT_ENTER = 'Enter'
    EVENT_LEAVE = 'Leave'
    EVENT_TIMEOUT = 'Timeout'
    EVENT_STATE_CHANGE = 'StateChange'

    """
    A state-machine based on a single state variable.
    Enforces optional state timeouts.
    Can generate internal leave, enter, and timeout events.
    """
    def __init__(self, obj, initial_state: str, state_timeouts: Dict[str,int]=None) -> None:
        super(State, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)

        if not obj:
            raise TypeError('This state does not have an owner object.')
        self.obj = obj

        if not initial_state:
            raise TypeError('This state does not have an initial state.')
        self.initial_state: str = initial_state

        self.current_state: str = None
        self.state_timeouts: Dict[str,int] = state_timeouts if state_timeouts else {}
        self.state_timer = None
        self.reset_state()

    def reset_state(self) -> None:
        """
        Set the current state to the initial state.
        """
        if not self.initial_state:
            raise TypeError('This state does not have an initial state.')

        self.log.info('Resetting state to ' + str(self.initial_state) + '.')
        self.current_state = self.initial_state
        self.stop_state_timer()

    def identify_state(self, event) -> str: #pylint: disable=unused-argument
        """
        Return the current state as the state variable.
        """

        return str(self.current_state)

    def change_state(self, new_state: str, notify: bool=False) -> None:
        """
        Transition to the new state and optionally notify listeners.
        The state transition will also generate and process internal leave and enter events.
        """

        if self.current_state is None:
            raise Exception('This state does not have a current state.')

        old_state = self.current_state

        # Only execute block if the state is really changing.
        if old_state != new_state:
            # Stop state timer.
            self.stop_state_timer()

            # Leave pseudo-event.
            Dispatcher().send(StateEvent(self.EVENT_LEAVE, new_state=new_state, old_state=old_state), self.obj, self.obj)

            # Change state.
            self.log.info('Changing state from %s to %s.' % (str(old_state), str(new_state)))
            self.current_state = new_state

            # Enter pseudo-event.
            Dispatcher().send(StateEvent(self.EVENT_ENTER, new_state=new_state, old_state=old_state), self.obj, self.obj)

            # Notify listeners.
            if notify:
                self.log.info('Notify listeners of the state change.')
                Dispatcher().notify(StateEvent(self.EVENT_STATE_CHANGE, new_state=new_state, old_state=old_state), self.obj)

            # Start state timer.
            self.start_state_timer()

    def start_state_timer(self) -> None:
        """
        If the current state is configured with a state timeout, then start the state timer.
        """

        state_timeout = self.state_timeouts.get(self.current_state, None)

        if state_timeout:
            self.log.info('Start state timer with a timeout of ' + str(state_timeout) + '.')

            if self.state_timer:
                self.stop_state_timer()

            self.state_timer = Dispatcher().schedule(state_timeout, StateEvent(self.EVENT_TIMEOUT, new_state=self.current_state), self.obj, self.obj)

    def stop_state_timer(self) -> None:
        """
        Stop the state timer if it is running.
        """

        if self.state_timer:
            self.log.info('Stop state timer.')

            self.state_timer.cancel()
            self.state_timer = None

    def __str__(self):
        return 'state: %s, timer: %s, timeouts: %s' % (str(self.current_state), str(self.state_timer), str(self.state_timeouts))
