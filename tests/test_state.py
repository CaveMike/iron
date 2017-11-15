#! /usr/bin/python
import logging
import sys
from context import Context
from dispatcher import Dispatcher
from state import State

class TestState:
    class SampleObj:
        STATE_STOPPED = 'Stopped'
        STATE_STARTED = 'Started'
        STATE_PAUSED = 'Paused'

        def __init__(self):
            self.log = logging.getLogger(self.__class__.__name__)

            self.last_handler = None
            self.state = State(self, self.STATE_STOPPED, {self.STATE_PAUSED : 30})

        def identify_state(self, event):
            return self.state.identify_state(event)

        # Commands
        @Dispatcher.event_handler
        def Start(self, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        @Dispatcher.event_handler
        def Stop(self, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        @Dispatcher.event_handler
        def Pause(self, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        # Stopped
        def inStopped_onStart(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')
            self.state.change_state(self.STATE_STARTED)

        def inStopped_onEnter(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inStopped_onLeave(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inStopped_onDefault(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        # Started
        def inStarted_onPause(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')
            self.state.change_state(self.STATE_PAUSED)

        def inStarted_onStop(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')
            self.state.change_state(self.STATE_STOPPED)

        def inStarted_onEnter(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inStarted_onLeave(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inStarted_onDefault(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        # Paused
        def inPaused_onStart(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')
            self.state.change_state(self.STATE_STARTED)

        def inPaused_onStop(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')
            self.state.change_state(self.STATE_STOPPED)

        def inPaused_onEnter(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inPaused_onLeave(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def inPaused_onDefault(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        # Default
        def onEnter(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def onLeave(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def onDefault(self, event, *args, **kwargs):
            self.last_handler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

    def test(self):
        d = Dispatcher()

        c = Context('Root')
        c.start()

        o = self.SampleObj()
        d.add(obj=o, parent_obj=None, context=c)

        o.Start()
        assert str(o.state.current_state) == o.STATE_STARTED
        assert str(o.last_handler) == 'inStarted_onEnter'
        o.Pause()
        assert str(o.state.current_state) == 'Paused'
        assert str(o.last_handler) == 'inPaused_onEnter'
        o.Stop()
        assert str(o.state.current_state) == 'Stopped'
        assert str(o.last_handler) == 'inStopped_onEnter'

        c.stop()
