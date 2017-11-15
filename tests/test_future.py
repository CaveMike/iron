#! /usr/bin/python
from iron.future import Future
from iron.future import ScheduledFuture

def sampleFunction(*args, **kwargs):
    return sum(args)

def sampleProcess(future):
    return future.process()

class TestFuture:
    def test(self):

        f = Future(sampleFunction, 1, 2, 3, x='X', y='Y', z='Z')
        f.process()
        assert f() == 6

        # Specify None for the function since it will never run.
        f = Future(None)
        f.cancel()
        assert f() is None

class TestScheduledFuture:
    def test(self):

        # Use 0 seconds so that the test runs quickly.
        f = ScheduledFuture(0, sampleProcess, sampleFunction, 3, 4, 5)
        assert f() == 12

        # Specify None for the functions since they will never run.
        f = ScheduledFuture(60, None, None)
        f.cancel()
        assert f() is None
