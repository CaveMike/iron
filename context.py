#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from iron.future import Future
from iron.future import ScheduledFuture
import Queue
import threading
import logging
import sys

class Context(object):
    def __init__( self, name ):
        super( Context, self ).__init__()
        self.log = logging.getLogger( self.__class__.__name__ )

        self.__queue = Queue.Queue()
        self.__thread = threading.Thread( None, self.run, name )

    def queue( self, event, srcObj, dstObj, *args, **kwargs ):
        """
        Queue an event to be processed by dstObj when the context's
        run() or poll() function is called.
        """
        if not dstObj:
            raise Exception( 'Cannot queue event, ' + str(event()) + ', without a destination.' )

        self.log.debug( 'Queue ' + str(event()) + '.' )
        future = Future( Dispatcher.send, event, srcObj, dstObj, *args, **kwargs )
        self.__queue.put( future )

        return future

    def schedule( self, seconds, event, srcObj, dstObj, *args, **kwargs ):
        """
        Schedule a timer that will queue an event after the specified number of seconds.
        """
        if not dstObj:
            raise Exception( 'Cannot schedule event, ' + str(event()) + ', without a destination.' )

        self.log.debug( 'Schedule ' + str(event()) + '.' )
        return ScheduledFuture( seconds, self.__queue.put, Dispatcher.send, event, srcObj, dstObj, *args, **kwargs )


    def start( self ):
        """
        Start the event processing thread.
        """
        self.log.debug( 'Start.' )
        self.__thread.start()

    def stop( self, timeout = None ):
        """
        Stop the event processing thread by queuing the termination event.
        """
        self.log.debug( 'Stop.' )

        # Add the termination event.
        self.__queue.put( None )

        # Wait for the thread to terminate.
        self.__thread.join( timeout )

        return not self.__thread.isAlive()

    def run( self ):
        """
        Start the event processing loop.
        The loop will continue until the termination event is processed.
        """
        while self.__process( block = True ):
            pass

    def poll( self ):
        """
        This function will process each event currently added in the queue.
        It is possible for other threads to add events to the queue while processing
        previous events.  The new events will be also processed.
        """
        while not self.__queue.empty():
            self.__process( block = False )

    def __process( self, block ):
        """
        Returns True if an item was processed.
        Returns False if the termination event was processed.
        """
        future = self.__queue.get( block )
        if future:
            self.log.info( 'Dequeue ' + str(future) + '.' )
            future.process()
            return True
        else:
            return False

    def __str__( self ):
        return 'name: %s, queue size: %s' % ( self.__thread.getName(), str(self.__queue.qsize()) )

