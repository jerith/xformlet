# -*- test-case-name: xformlet.tests.test_events -*-

from datetime import datetime


#################################################
# Event machinery


class DOMEventFlowManager(object):
    def __init__(self, dom_tree):
        self.dom_tree = dom_tree
        self._listeners = {}
        self._actions = {}

    def set_default_action(self, target, event_type, listener):
        default_actions = self._actions.setdefault(target, [])
        listener_tuple = (event_type, listener)
        if listener_tuple not in default_actions:
            default_actions.append(listener_tuple)

    def add_event_listener(self, target, event_type, listener, capture):
        listeners = self._listeners.setdefault(target, [])
        listener_tuple = (event_type, listener, capture)
        if listener_tuple not in listeners:
            listeners.append(listener_tuple)

    def remove_event_listener(self, target, event_type, listener, capture):
        listeners = self._listeners.setdefault(target, [])
        listener_tuple = (event_type, listener, capture)
        if listener_tuple in listeners:
            listeners.remove(listener_tuple)

    def dispatch_event(self, target, event):
        event.target = target
        event.timestamp = datetime.utcnow()

        # We don't want to include the actual target in event_path, but we need
        # to start with it in case it's the root node and has no parent.
        event_path = [target]
        while event_path[-1].get_parents():
            event_path.append(event_path[-1].get_parents()[0])
        event_path = event_path[1:]

        event.event_phase = DOMEvent.CAPTURING_PHASE
        self._do_event_flow(reversed(event_path), event)

        if not event._stopped:
            event.event_phase = DOMEvent.AT_TARGET
            self._deliver_event(target, event)
            self._handle_default_action(event)

        if event.can_bubble:
            event.event_phase = DOMEvent.BUBBLING_PHASE
            self._do_event_flow(event_path, event)

    def _do_event_flow(self, event_path, event):
        for node in event_path:
            if event._stopped:
                return
            self._deliver_event(node, event)

    def _deliver_event(self, node, event):
        event.current_target = node
        for event_type, listener, capture in self._listeners.get(node, []):
            if event_type != event.event_type:
                continue
            if capture != (event.event_phase == DOMEvent.CAPTURING_PHASE):
                continue
            listener(event)

    def _handle_default_action(self, event):
        if event._canceled:
            return

        for event_type, listener in self._actions.get(event.target, []):
            if event_type == event.event_type:
                listener(event)


class DOMEvent(object):
    (CAPTURING_PHASE, AT_TARGET, BUBBLING_PHASE) = (1, 2, 3)

    EVENT_TYPE = None
    CAN_BUBBLE = None
    CANCELABLE = None

    def __init__(self):
        self.event_type = self.EVENT_TYPE
        self.can_bubble = self.CAN_BUBBLE
        self.cancelable = self.CANCELABLE

        assert self.event_type is not None
        assert self.can_bubble is not None
        assert self.cancelable is not None

        self.target = None
        self.current_target = None
        self.event_phase = None
        self.timestamp = None

        self._canceled = False
        self._stopped = False

    def __repr__(self):
        return (
            '<%s type=%r can_bubble=%s cancelable=%s '
            'target=%s current=%s canceled=%s stopped=%s>') % (
            type(self).__name__, self.event_type, self.can_bubble,
            self.cancelable, self.target, self.current_target, self._canceled,
            self._stopped)

    def prevent_default(self):
        if self.cancelable:
            self._canceled = True

    def stop_propagation(self):
        self._stopped = True


def make_event_type(base_class, event_type, cancelable, can_bubble):
    class_name = "%s_%s" % (base_class.__name__, event_type.replace('-', '_'))
    globals()[class_name] = type(class_name, (base_class,), {
        'EVENT_TYPE': event_type,
        'CANCELABLE': cancelable,
        'CAN_BUBBLE': can_bubble,
        })
    return globals()[class_name]


#################################################
# Event types


# Initialization events

class XFormsInitializationEvent(DOMEvent):
    pass


def make_init_event(*args):
    make_event_type(XFormsInitializationEvent, *args)

make_init_event('xforms-model-construct', False, True)
make_init_event('xforms-model-construct-done', False, True)
make_init_event('xforms-ready', False, True)
make_init_event('xforms-model-destruct', False, True)


# Interaction events

class XFormsInteractionEvent(DOMEvent):
    pass


def make_interact_event(*args):
    make_event_type(XFormsInteractionEvent, *args)

make_interact_event('xforms-rebuild', True, True)
make_interact_event('xforms-recalculate', True, True)
make_interact_event('xforms-revalidate', True, True)
make_interact_event('xforms-refresh', True, True)
make_interact_event('xforms-reset', True, True)
make_interact_event('xforms-previous', True, False)
make_interact_event('xforms-next', True, False)
make_interact_event('xforms-focus', True, False)
make_interact_event('xforms-help', True, True)
make_interact_event('xforms-hint', True, True)
make_interact_event('xforms-submit', True, True)
make_interact_event('xforms-submit-serialize', False, True)


# Notification events

class XFormsNotificationEvent(DOMEvent):
    pass


def make_notify_event(*args):
    make_event_type(XFormsNotificationEvent, *args)

make_notify_event('xforms-insert', False, True)
make_notify_event('xforms-delete', False, True)
make_notify_event('xforms-value-change', False, True)
make_notify_event('xforms-valid', False, True)
make_notify_event('xforms-invalid', False, True)
make_notify_event('xforms-readonly', False, True)
make_notify_event('xforms-readwrite', False, True)
make_notify_event('xforms-required', False, True)
make_notify_event('xforms-optional', False, True)
make_notify_event('xforms-enabled', False, True)
make_notify_event('xforms-disabled', False, True)
make_notify_event('DOMActivate', True, True)
make_notify_event('DOMFocusIn', False, True)
make_notify_event('DOMFocusOut', False, True)
make_notify_event('xforms-select', False, True)
make_notify_event('xforms-deselect', False, True)
make_notify_event('xforms-in-range', False, True)
make_notify_event('xforms-out-of-range', False, True)
make_notify_event('xforms-scroll-first', False, True)
make_notify_event('xforms-scroll-last', False, True)
make_notify_event('xforms-submit-done', False, True)


# Error indications

class XFormsErrorEvent(DOMEvent):
    pass


def make_error_event(*args):
    make_event_type(XFormsErrorEvent, *args)

make_error_event('xforms-binding-exception', False, True)
make_error_event('xforms-compute-exception', False, True)
make_error_event('xforms-version-exception', False, True)
make_error_event('xforms-link-exception', False, True)
make_error_event('xforms-output-error', False, True)
make_error_event('xforms-submit-error', False, True)
