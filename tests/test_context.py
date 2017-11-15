#! /usr/bin/python
import copy
import time
from event import Event
from context import Context

class SampleObj():
    def __init__(self, events):
        self.events = copy.copy(events)

    def process(self, event, *args, **kwargs):
        expected = self.events.pop(0)
        assert expected == event
        return 'Processed ' + event()

class TestContextThreaded:
    def test(self):
        events = [Event('event0'), Event('event1'), Event('event2')]

        o = SampleObj(events)

        c = Context('context0')
        c.start()

        for event in events:
            future = c.queue(event, o, o)
            #print future
            #future.cancel()
            #print future()
            #print future
        time.sleep(0.1)

        c.stop()

class TestContextPolled:
    def test(self):
        events = [Event('event0'), Event('event1'), Event('event2')]

        o = SampleObj(events)

        c = Context('context0')

        for event in events:
            future = c.queue(event, o, o)
        time.sleep(0.1)

        c.poll()
