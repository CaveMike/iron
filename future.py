#!/usr/bin/env python
import copy
import logging
import sys
import threading

class Future(object):
    """
    A future that is used when queuing events in a Context.
    The future can be used to determine the result of the event processing.

    This implementation is based on:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/84317
        Based on implementation by David Perry and modifications by Bjorn Pettersen and Graham Horler.
    """

    STATE_ACTIVE    = 'Active'
    STATE_COMPLETED = 'Completed'
    STATE_CANCELLED = 'Cancelled'
    STATE_EXCEPTION = 'Exception'

    def __init__( self, function, *args, **kwargs ):
        super( Future, self ).__init__()
        self.log = logging.getLogger( self.__class__.__name__ )

        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.__state = self.STATE_ACTIVE
        self.__result = None
        self.__excpt  = None

        # Notify using this Condition when the result is ready.
        self._condition = threading.Condition()

    def __call__( self ):
        """
        If the event is done being processed, return the result;
        otherwise, block.  If the future was cancelled while blocking,
        return None.  If an exception was thrown while processing the
        event, throw it here.
        """

        self.log.debug( '__call__' )

        self._condition.acquire()
        while self.__state == self.STATE_ACTIVE:
            # Block until the future is complete.
            self._condition.wait()
        self._condition.release()

        # An exception was thrown in the thread, re-raise it here.
        if self.__excpt:
            raise self.__excpt

        if self.__state == self.STATE_CANCELLED:
            return None

        # Copy the __result to prevent accidental tampering with it.
        # Use deepcopy to get the entire result.
        return copy.deepcopy( self.__result )

    def cancel( self ):
        """
        If a future is blocked and waiting for its result, cancel it.
        This future will return a result of None to the blocked thread.
        """

        self.log.debug( 'cancel' )

        # Assume the future cannot be cancelled.
        cancelled = False

        self._condition.acquire()

        # The future can be cancelled if it is only in the active state.
        if self.__state == self.STATE_ACTIVE:
            self.__state = self.STATE_CANCELLED
            self._condition.notify()
            cancelled = True

        self._condition.release()

        # Return if it was successfully cancelled.
        return cancelled

    def process( self ):
        """
        Process an event and save the result.
        """

        self.log.debug( 'process' )

        self._condition.acquire()

        if self.__state == self.STATE_ACTIVE:
            try:
                self.__result = self.function( *self.args, **self.kwargs )
                self.__state = self.STATE_COMPLETED
            except Exception, e:
                self.log.error( 'process has thrown an exception, ' + str(e) + '.' )
                self.__result = self.STATE_EXCEPTION
                self.__excpt = sys.exc_info()

        self._condition.notify()
        self._condition.release()

    def __str__( self ):
        return 'state: %s, result: %s, exception: %s' % ( str(self.__state), str(self.__result), str(self.__excpt) )

class ScheduledFuture(Future):
    """
    The ScheduledFuture object allows applications to track the results of an
    operation that not only takes a finite amount of time to run, but will not
    even be scheduled to run for a number of seconds.

    A normal Future object cannot be used for this purpose since an application
    may want to cancel the future at one of two times:
       1. While the timer is pending (before the operation is started).
       2. While the operation is running.
    ScheduledFuture extends Future by allowing it to cancel the future at
    either of these points in time.

    After the specified seconds, scheduleFunction will be run.  This function
    should call (or eventually cause to call) ScheduledFuture.process().
    As with a normal future, ScheduledFuture.process() will call function.
    """

    def __init__( self, seconds, scheduleFunction, function, *args, **kwargs ):
        super( ScheduledFuture, self ).__init__( function, *args, **kwargs )
        self.log = logging.getLogger( self.__class__.__name__ )

        self.scheduleFunction = scheduleFunction

        self.timer = threading.Timer( seconds, self.__timeout )
        self.timer.start()

    def __timeout( self ):
        """
        The timeout handler that queues the event for processing.
        """

        self.log.debug( '__timeout' )

        self.timer = None
        self.scheduleFunction( self )

    def cancel( self ):
        """
        If the timer is still running, cancel the timer and do not queue the
        event for processing.
        Then cancel the base Future object.
        """

        self.log.debug( 'cancel' )

        if self.timer:
            # If a valid timer exists, then cancel it.
            self.timer.cancel()
            self.timer = None

        return super( ScheduledFuture, self ).cancel()

class FutureMimic(object):
    """
    The FutureMimic class is necessary to mimic the Future object.
    This allows applications to treat futures and non-futures
        the exact same way.
    """

    def __init__( self, result ):
        self.result = result

    def __call__( self ):
        return self.result

    def __str__( self ):
        return str(self.result)

