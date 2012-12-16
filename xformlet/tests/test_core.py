from unittest import TestCase

from xformlet.core import XFormsEngine
from xformlet.tests.utils import make_doc


class XFormsEngineTestCase(TestCase):
    def test_engine_setup(self):
        engine = XFormsEngine(make_doc('<xforms:model />'))
        self.assertEqual(len(engine._models), 1)

        engine = XFormsEngine(make_doc('<xforms:model /><xforms:model />'))
        self.assertEqual(len(engine._models), 2)
