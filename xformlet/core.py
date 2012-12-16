# -*- test-case-name: xformlet.tests.test_core -*-

from xpathlet.engine import build_xpath_tree, ExpressionEngine

from xformlet.function_library import XFormsFunctionLibrary
from xformlet.events import DOMEventFlowManager


NAMESPACES = (
    ('xforms', 'http://www.w3.org/2002/xforms'),
    ('ev', 'http://www.w3.org/2001/xml-events'),
    )


def event_handler(event_type):
    def deco(func):
        func.handles_event = event_type
        return func
    return deco


class XFormsElement(object):
    def __init__(self, engine, xpath_node):
        self.engine = engine
        self.xpath_node = xpath_node
        self._setup_event_handlers()
        self.setup()

    def _setup_event_handlers(self):
        for name in dir(self):
            obj = getattr(self, name)
            if callable(obj) and hasattr(obj, 'handles_event'):
                self.set_event_action(obj.handles_event, obj)

    def setup(self):
        pass

    def set_event_action(self, event_type, listener):
        self.engine.doc_event_manager.set_default_action(
            self.xpath_node, event_type, listener)


class XFormsModel(XFormsElement):

    @event_handler('xforms-model-construct')
    def event_construct(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-construct-done')
    def event_construct_done(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-rebuild')
    def event_rebuild(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-recalculate')
    def event_recalculate(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-revalidate')
    def event_revalidate(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-refresh')
    def event_refresh(self, event):
        raise NotImplementedError()

    @event_handler('xforms-model-reset')
    def event_reset(self, event):
        raise NotImplementedError()


class XFormsInstance(XFormsElement):
    pass


class XFormsSubmission(XFormsElement):
    pass


class XFormsBind(XFormsElement):
    pass


class XFormsEngine(object):
    # NOTE: This assumes the document itself does not change underneath us.

    def __init__(self, xform_doc_file):
        self.doc_tree = build_xpath_tree(xform_doc_file)
        self.doc_engine = ExpressionEngine(
            self.doc_tree, variables={},
            function_libraries=[XFormsFunctionLibrary()])
        self.doc_event_manager = DOMEventFlowManager(self.doc_tree)

        self._xev_cache = {}

        self._models = {}
        for model_node in self.xev('//xforms:model', self.doc_tree):
            self._models[model_node] = XFormsModel(self, model_node)

    def xev(self, expr, node=None, pos=1, size=1, replace_namespaces=True):
        if replace_namespaces:
            expr = self._replace_namespaces(expr)
        ckey = (expr, node, pos, size)
        if ckey not in self._xev_cache:
            self._xev_cache[ckey] = self.doc_engine.evaluate(
                expr, node, context_position=pos, context_size=size).value
        return self._xev_cache[ckey]

    def _replace_namespaces(self, expr):
        for expr_prefix, expr_uri in NAMESPACES:
            for prefix, uri in self.doc_tree._namespaces.items():
                if uri == expr_uri:
                    expr = expr.replace(
                        '%s:' % (expr_prefix,), '%s:' % (prefix,))
                    break
        return expr
