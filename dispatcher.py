#!/usr/bin/env python
from carbon.helpers import getCaller
from carbon.singletonmixin import Singleton
from iron.delegator import Delegator
from iron.event import Event
from iron.future import FutureMimic
import logging

class Dispatcher(Singleton):
    class Node(object):
        """
        An reference to an object that processes events by finding and calling
        an appropriate event handler.
        """
        def __init__( self, obj, parent, context ):
            super( Dispatcher.Node, self ).__init__()
            self.log = logging.getLogger( self.__class__.__name__ )

            self.obj = obj
            self.parent = parent
            self.context = context
            self.listeners = set()

        def __str__( self ):
            return 'obj: %s, parent: %s, context: %s, listeners: %s' % ( str(self.obj), str(self.parent), str(self.context), str(len(self.listeners)) )

    """
    A simple dispatcher that can send events from one object to another.
    The dispatcher creates a helper node for each object.  This node is used to
    find and dispatch events and manage the object's context.  Nodes are also
    organized in a parent-child relationship so that objects can send events to
    their parents.
    """
    def __init__( self ):
        super( Dispatcher, self ).__init__()
        self.log = logging.getLogger( self.__class__.__name__ )

        self.nodes = {}

    @staticmethod
    def add( obj, parentObj = None, context = None ):
        """
        Add an object to the dispatcher.
        """
        # If an object is not specified, raise an exception.
        if not obj:
            raise Exception( 'A node cannot be added without an object.' )

        self = Dispatcher.getInstance()

        # If a context is not specified, get the parent's context.
        if not context:
            if parentObj:
                parentNode = self._getNode( parentObj )
                if parentNode:
                    context = parentNode.context

        if not context:
            raise Exception( 'A node cannot be added without a context.  Failed to find the context for the object, ' + str(obj) + '.' )

        node = self.Node( obj, parentObj, context )
        self.nodes[obj] = node

    @staticmethod
    def remove( obj ):
        # If an object is not specified, raise an exception.
        self = Dispatcher.getInstance()

        if not obj:
            raise Exception( 'A node cannot be added without an object.' )

        #FIXME: This obj could still be added as a listener to other objects.
        del self.nodes[obj]

    @staticmethod
    def send( event, srcObj, dstObj, *args, **kwargs ):
        """
        Send an event to a dstObj object.
        If the dstObj object is in the same context, the event will be processed right away.
        Otherwise, the event will be queued and processed later.
        """
        self = Dispatcher.getInstance()

        self.log.debug( 'Send event, ' + str(event()) + '.' )

        if not event:
            raise Exception( 'Must specify an event.' )

        if srcObj is None:
            srcObj = getCaller()

        srcNode = self._getNode( srcObj )
        dstNode = self._getNode( dstObj )

        return self._send( event, srcNode, dstNode, queued = False, *args, **kwargs )

    @staticmethod
    def queue( event, srcObj, dstObj, *args, **kwargs ):
        """
        Send an event to a dstObj object.
        The event will always be queued and processed later.
        """
        self = Dispatcher.getInstance()

        self.log.debug( 'Queue event, ' + str(event()) + '.' )

        if not event:
            raise Exception( 'Must specify an event.' )

        if srcObj is None:
            srcObj = getCaller()

        srcNode = self._getNode( srcObj )
        dstNode = self._getNode( dstObj )

        return self._send( event, srcNode, dstNode, queued = True, *args, **kwargs )

    @staticmethod
    def schedule( seconds, event, srcObj, dstObj, *args, **kwargs ):
        """
        Schedule an event to be sent to a dstObj.
        The event will always be queued.
        Returns a Timer object for the event.  The Timer object can be used to cancel the event.
        """
        self = Dispatcher.getInstance()

        self.log.debug( 'Schedule event, ' + str(event()) + ', for ' + str(seconds) + ' seconds.' )

        if not event:
            raise Exception( 'Must specify an event.' )

        if srcObj is None:
            srcObj = getCaller()

        srcNode = self._getNode( srcObj )
        dstNode = self._getNode( dstObj )

        if not dstNode.context:
            raise TypeError( 'This destination node does not have a context.' )

        return dstNode.context.schedule( seconds, event, srcNode.obj, dstNode.obj, *args, **kwargs )

    @staticmethod
    def addListener( srcObj, dstObj ):
        self = Dispatcher.getInstance()

        srcNode = self._getNode( srcObj )
        dstNode = self._getNode( dstObj )

        #FIXME: Need to use a WeakSet or similar.
        srcNode.listeners.add( dstNode )

    @staticmethod
    def removeListener( srcObj, dstObj ):
        self = Dispatcher.getInstance()

        srcNode = self._getNode( srcObj )
        dstNode = self._getNode( dstObj )

        srcNode.listeners.discard( dstNode )

    @staticmethod
    def notify( event, srcObj = None, *args, **kwargs ):
        """
        Send an event to the parent.
        """
        self = Dispatcher.getInstance()

        if not event:
            raise Exception( 'Must specify an event.' )

        if srcObj is None:
            srcObj = getCaller()

        srcNode = self._getNode( srcObj )

        from carbon.helpers import curry

        for dstNode in srcNode.listeners:
            self._send( event, srcNode, dstNode, queued=True, *args, **kwargs )

    def _delegate( self, event, obj, *args, **kwargs ):
        """
        Process a single event by dispatching the event to the best-fitting event-handler.
        If an event-handler is not available, return None otherwise return the result of the processing.
        """
        self.log.debug( 'Process event, ' + str(event()) + '.' )

        function = Delegator.getHandler( obj, event )
        if function:
            self.log.info( 'Dispatching event, ' + str(event()) + ', to function, ' + str(function.__name__) + '.' )
            return function( event, *args, **kwargs )
        else:
            self.log.debug( 'Unhandled event, ' + str(event()) + '.' )
            return None

    def _send( self, event, srcNode, dstNode, queued, *args, **kwargs ):
        """
        A helper function to send events to a node.
        """
        if srcNode.context != dstNode.context:
            # The nodes belong to different contexts, so this message must be queued.
            queued = True

        if not queued:
            result = self._delegate( event, dstNode.obj, *args, **kwargs )
            # Wrap the result in a FutureMimic object to mimic the behavior of a Future object.
            return FutureMimic( result )
        else:
            if not dstNode.context:
                raise TypeError( 'This destination node does not have a context.' )

            return dstNode.context.queue( event, srcNode.obj, dstNode.obj, *args, **kwargs )

    def _getNode( self, obj ):
        if not obj:
            raise Exception( 'Must specify an object.' )

        node = self.nodes[obj]
        if not node:
            raise Exception( 'Cannot find the node for object, ' + str(obj) + '.' )

        return node

    def __str__( self ):
        return '\n'.join( [ str(node) for node in self.nodes.itervalues() ] )

    @staticmethod
    def eventHandler( func ):
        """
        A decorator that can be used to redirect a standard method
        call to the internal event processing.

        For example:
            @Dispatcher.eventHandler
            def greenButtonPushed( self, *args, **kwargs ):
                print 'Green button pushed.'

        Will be changed to:
            def greenButtonPushed( self, *args, **kwargs ):
                print 'Green button pushed.'
                Dispatcher.getInstance().send( 'greenButtonPushed', self, self, *args, **kwargs )
        """

        def process( self, *args, **kwargs ):
            self.log.debug( 'Call process ' + str(func.__name__) + '.' )
            func( self, *args, **kwargs )
            return Dispatcher.getInstance().send( Event(func.__name__), self, self, *args, **kwargs )
        return process

