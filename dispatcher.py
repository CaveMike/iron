#!/usr/bin/env python3
import inspect
import logging
from typing import Dict, Generic, TypeVar
from delegator import Delegator
from event import Event
from future import FutureMimic

NodeType = TypeVar('NodeType')
NodeDictType = Dict[object, NodeType]

class Singleton(type):
    _instances: NodeDictType = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Dispatcher(metaclass=Singleton):

    """
    A simple dispatcher that can send events from one object to another.
    The dispatcher creates a helper node for each object.  This node is used to
    find and dispatch events and manage the object's context.  Nodes are also
    organized in a parent-child relationship so that objects can send events to
    their parents.
    """
    class Node(Generic[NodeType]):
        """
        An reference to an object that processes events by finding and calling
        an appropriate event handler.
        """
        def __init__(self, obj, parent, context):
            super(Dispatcher.Node, self).__init__()
            self.log = logging.getLogger(self.__class__.__name__)

            self.obj = obj
            self.parent = parent
            self.context = context
            self.listeners = set()

        def __str__(self):
            return 'obj: %s, parent: %s, context: %s, listeners: %s' % (str(self.obj), str(self.parent), str(self.context), str(len(self.listeners)))

    def __init__(self) -> None:
        super(Dispatcher, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)

        self.nodes: NodeDictType={}

    @staticmethod
    def get_caller():
        try:
            return inspect.stack()[2][0].f_locals['self']
        except KeyError:
            pass

        return None

    @staticmethod
    def add(obj, parent_obj=None, context: object=None):
        """
        Add an object to the dispatcher.
        """
        # If an object is not specified, raise an exception.
        if not obj:
            raise Exception('A node cannot be added without an object.')

        self = Dispatcher()

        # If a context is not specified, get the parent's context.
        if not context:
            if parent_obj:
                parent_node = self.get_node(parent_obj)
                if parent_node:
                    context = parent_node.context

        if not context:
            raise Exception('A node cannot be added without a context.  Failed to find the context for the object, ' + str(obj) + '.')

        node: Dispatcher.Node = self.Node(obj, parent_obj, context)
        self.nodes[obj] = node

    @staticmethod
    def remove(obj):
        # If an object is not specified, raise an exception.
        self = Dispatcher()

        if not obj:
            raise Exception('A node cannot be added without an object.')

        #FIXME: This obj could still be added as a listener to other objects.
        del self.nodes[obj]

    @staticmethod
    def send(event, src_obj, dst_obj, *args, **kwargs):
        """
        Send an event to a dst_obj object.
        If the dst_obj object is in the same context, the event will be processed right away.
        Otherwise, the event will be queued and processed later.
        """
        self = Dispatcher()

        self.log.debug('Send event, ' + str(event()) + '.')

        if not event:
            raise Exception('Must specify an event.')

        if src_obj is None:
            src_obj = Dispatcher.get_caller()

        src_node = self.get_node(src_obj)
        dst_node = self.get_node(dst_obj)

        return self.send_internal(event, src_node, dst_node, queued=False, *args, **kwargs)

    @staticmethod
    def queue(event, src_obj, dst_obj, *args, **kwargs):
        """
        Send an event to a dst_obj object.
        The event will always be queued and processed later.
        """
        self = Dispatcher()

        self.log.debug('Queue event, ' + str(event()) + '.')

        if not event:
            raise Exception('Must specify an event.')

        if src_obj is None:
            src_obj = Dispatcher.get_caller()

        src_node = self.get_node(src_obj)
        dst_node = self.get_node(dst_obj)

        return self.send_internal(event, src_node, dst_node, queued=True, *args, **kwargs)

    @staticmethod
    def schedule(seconds, event, src_obj, dst_obj, *args, **kwargs):
        """
        Schedule an event to be sent to a dst_obj.
        The event will always be queued.
        Returns a Timer object for the event.  The Timer object can be used to cancel the event.
        """
        self = Dispatcher()

        self.log.debug('Schedule event, ' + str(event()) + ', for ' + str(seconds) + ' seconds.')

        if not event:
            raise Exception('Must specify an event.')

        if src_obj is None:
            src_obj = Dispatcher.get_caller()

        src_node = self.get_node(src_obj)
        dst_node = self.get_node(dst_obj)

        if not dst_node.context:
            raise TypeError('This destination node does not have a context.')

        return dst_node.context.schedule(seconds, event, src_node.obj, dst_node.obj, *args, **kwargs)

    @staticmethod
    def add_listener(src_obj, dst_obj):
        self = Dispatcher()

        src_node = self.get_node(src_obj)
        dst_node = self.get_node(dst_obj)

        #FIXME: Need to use a WeakSet or similar.
        src_node.listeners.add(dst_node)

    @staticmethod
    def remove_listener(src_obj, dst_obj):
        self = Dispatcher()

        src_node = self.get_node(src_obj)
        dst_node = self.get_node(dst_obj)

        src_node.listeners.discard(dst_node)

    @staticmethod
    def notify(event, src_obj=None, *args, **kwargs):
        """
        Send an event to the parent.
        """
        self = Dispatcher()

        if not event:
            raise Exception('Must specify an event.')

        if src_obj is None:
            src_obj = Dispatcher.get_caller()

        src_node = self.get_node(src_obj)

        for dst_node in src_node.listeners:
            self.send_internal(event, src_node, dst_node, queued=True, *args, **kwargs)

    def _delegate(self, event, obj, *args, **kwargs):
        """
        Process a single event by dispatching the event to the best-fitting event-handler.
        If an event-handler is not available, return None otherwise return the result of the processing.
        """
        self.log.debug('Process event, ' + str(event()) + '.')

        function = Delegator.get_handler(obj, event)
        if function:
            self.log.info('Dispatching event, ' + str(event()) + ', to function, ' + str(function.__name__) + '.')
            return function(event, *args, **kwargs)
        else:
            self.log.debug('Unhandled event, ' + str(event()) + '.')
            return None

    def send_internal(self, event, src_node, dst_node, queued, *args, **kwargs):
        """
        A helper function to send events to a node.
        """
        if src_node.context != dst_node.context:
            # The nodes belong to different contexts, so this message must be queued.
            queued = True

        if not queued:
            result = self._delegate(event, dst_node.obj, *args, **kwargs)
            # Wrap the result in a FutureMimic object to mimic the behavior of a Future object.
            return FutureMimic(result)
        else:
            if not dst_node.context:
                raise TypeError('This destination node does not have a context.')

            return dst_node.context.queue(event, src_node.obj, dst_node.obj, *args, **kwargs)

    def get_node(self, obj):
        if not obj:
            raise Exception('Must specify an object.')

        node = self.nodes[obj]
        if not node:
            raise Exception('Cannot find the node for object, ' + str(obj) + '.')

        return node

    def __str__(self):
        return '\n'.join([str(node) for node in self.nodes.values()])

    @staticmethod
    def event_handler(func):
        """
        A decorator that can be used to redirect a standard method
        call to the internal event processing.

        For example:
            @Dispatcher.event_handler
            def greenButtonPushed(self, *args, **kwargs):
                print 'Green button pushed.'

        Will be changed to:
            def greenButtonPushed(self, *args, **kwargs):
                print 'Green button pushed.'
                Dispatcher().send('greenButtonPushed', self, self, *args, **kwargs)
        """

        def process(self, *args, **kwargs):
            self.log.debug('Call process ' + str(func.__name__) + '.')
            func(self, *args, **kwargs)
            return Dispatcher().send(Event(func.__name__), self, self, *args, **kwargs)
        return process
