#! /usr/bin/python
import logging
import sys
from event import Event
from dispatcher import Dispatcher
from context import Context

class TestDispatcher:
    class SampleObj:
        def __init__(self):
            self.log = logging.getLogger(self.__class__.__name__)
            self.lastHandler = None

        def on1(self, event, *args, **kwargs):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def on2(self, event, *args, **kwargs):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def on4(self, event, *args, **kwargs):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

        def onDefault(self, event, *args, **kwargs):
            self.lastHandler = sys._getframe().f_code.co_name
            self.log.debug(sys._getframe().f_code.co_name + '')

    def test(self):
        c = Context('Root')
        c.start()

        o0 = self.SampleObj()
        Dispatcher.add(obj=o0, parent_obj=None, context=c)

        o1 = self.SampleObj()
        Dispatcher.add(obj=o1, parent_obj=None, context=c)
        Dispatcher.add_listener(src_obj=o1, dst_obj=o0)

        Dispatcher.send(event=Event('1'), src_obj=o0, dst_obj=o1)
        assert str(o1.lastHandler) == 'on1'

        Dispatcher.queue(event=Event('2'), src_obj=o0, dst_obj=o1)
        #assert str(o1.lastHandler) == 'on2'

        Dispatcher.send(event=Event('3'), src_obj=o0, dst_obj=o1)
        #assert str(o1.lastHandler) == 'on3'

        Dispatcher.notify(event=Event('4'), src_obj=o1)
        #assert str(o1.lastHandler) == 'on4'
        Dispatcher.notify(event=Event('4'), src_obj=o1)
        #assert str(o1.lastHandler) == 'on4'

        c.stop()
