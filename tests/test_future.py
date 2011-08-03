#! /usr/bin/python
from iron.future import Future
from iron.future import ScheduledFuture
import logging
import sys
import unittest

def testFunction( *args, **kwargs ):
    return args[0] + args[1] + args[2]

def testProcess( future ):
    return future.process()

class TestFuture(unittest.TestCase):
    def runTest( self ):

        f = Future( testFunction, 1, 2, 3, x = 'X', y = 'Y', z = 'Z' )
        f.process()
        assert( f() == 6 )

        # Specify None for the function since it will never run.
        f = Future( None )
        f.cancel()
        assert( f() == None )

class TestScheduledFuture(unittest.TestCase):
    def runTest( self ):

        # Use 0 seconds so that the test runs quickly.
        f = ScheduledFuture( 0, testProcess, testFunction, 3, 4, 5 )
        assert( f() == 12 )

        # Specify None for the functions since they will never run.
        f = ScheduledFuture( 60, None, None )
        f.cancel()
        assert( f() == None )

if __name__ == '__main__':
    logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()

