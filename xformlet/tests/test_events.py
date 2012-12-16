from unittest import TestCase

from xpathlet.engine import build_xpath_tree, ExpressionEngine

from xformlet.events import DOMEvent, DOMEventFlowManager
from xformlet.tests.utils import make_doc


EVENTS_XML = '\n'.join([
    '<elem1>',
    '  <elem2>',
    '    <elem3>',
    '    </elem3>',
    '  </elem2>',
    '</elem1>',
    ])


class ToyEvent(DOMEvent):
    EVENT_TYPE = 'toy-event'
    CAN_BUBBLE = False
    CANCELABLE = True


class BubbleEvent(DOMEvent):
    EVENT_TYPE = 'bubble-event'
    CAN_BUBBLE = True
    CANCELABLE = True


class DOMEventFlowManagerTestCase(TestCase):
    def setUp(self):
        self.doc = build_xpath_tree(make_doc(EVENTS_XML))
        self.engine = ExpressionEngine(self.doc)
        self.manager = DOMEventFlowManager(self.doc)

    def get_node(self, expr):
        [node] = self.engine.evaluate(expr, self.doc).value
        return node

    def add_listener(self, target_expr, event_type, listener, capture=False):
        target = self.get_node(target_expr)
        self.manager.add_event_listener(target, event_type, listener, capture)

    def make_incr_handler(self, data, key):
        def handler(event):
            data.setdefault(key, 0)
            data[key] += 1
        return handler

    def test_dispatch_events_no_listeners(self):
        self.manager.dispatch_event(self.get_node('/'), ToyEvent())
        self.manager.dispatch_event(self.get_node('//elem1'), ToyEvent())
        self.manager.dispatch_event(self.get_node('//elem2'), ToyEvent())
        self.manager.dispatch_event(self.get_node('//elem3'), ToyEvent())

    def test_dispatch_event_target_listeners(self):
        data = {}
        listener1 = self.make_incr_handler(data, 'listener1')
        listener2 = self.make_incr_handler(data, 'listener2')
        self.add_listener('//elem1', 'toy-event', listener1)
        self.add_listener('//elem2', 'toy-event', listener1)
        self.add_listener('//elem3', 'toy-event', listener1)
        self.add_listener('//elem2', 'toy-event', listener2)

        self.assertEqual(data, {})
        self.manager.dispatch_event(self.get_node('//elem2'), ToyEvent())
        self.assertEqual(data, {'listener1': 1, 'listener2': 1})

    def test_dispatch_event_target_and_bubble_listeners(self):
        data = {}
        listener1 = self.make_incr_handler(data, 'listener1')
        listener2 = self.make_incr_handler(data, 'listener2')
        self.add_listener('//elem1', 'bubble-event', listener1)
        self.add_listener('//elem2', 'bubble-event', listener1)
        self.add_listener('//elem3', 'bubble-event', listener1)
        self.add_listener('//elem2', 'bubble-event', listener2)

        self.assertEqual(data, {})
        self.manager.dispatch_event(self.get_node('//elem2'), BubbleEvent())
        self.assertEqual(data, {'listener1': 2, 'listener2': 1})

    def test_dispatch_event_bubble_listeners(self):
        data = {}
        listener1 = self.make_incr_handler(data, 'listener1')
        self.add_listener('//elem1', 'bubble-event', listener1)
        self.add_listener('//elem2', 'bubble-event', listener1)

        self.assertEqual(data, {})
        self.manager.dispatch_event(self.get_node('//elem3'), BubbleEvent())
        self.assertEqual(data, {'listener1': 2})

    def test_dispatch_event_target_capture_listeners(self):
        data = {}
        listener1 = self.make_incr_handler(data, 'listener1')
        listener2 = self.make_incr_handler(data, 'listener2')
        self.add_listener('//elem1', 'toy-event', listener1, True)
        self.add_listener('//elem2', 'toy-event', listener1, True)
        self.add_listener('//elem3', 'toy-event', listener1, True)
        self.add_listener('//elem2', 'toy-event', listener2)

        self.assertEqual(data, {})
        self.manager.dispatch_event(self.get_node('//elem2'), ToyEvent())
        self.assertEqual(data, {'listener1': 1, 'listener2': 1})

    def test_dispatch_event_target_capture_bubble_listeners(self):
        data = {}
        listener1 = self.make_incr_handler(data, 'listener1')
        listener2 = self.make_incr_handler(data, 'listener2')
        self.add_listener('//elem1', 'bubble-event', listener1, True)
        self.add_listener('//elem2', 'bubble-event', listener1, True)
        self.add_listener('//elem3', 'bubble-event', listener1, True)
        self.add_listener('//elem1', 'bubble-event', listener2)
        self.add_listener('//elem2', 'bubble-event', listener2)
        self.add_listener('//elem3', 'bubble-event', listener2)

        self.assertEqual(data, {})
        self.manager.dispatch_event(self.get_node('//elem2'), BubbleEvent())
        self.assertEqual(data, {'listener1': 1, 'listener2': 2})
