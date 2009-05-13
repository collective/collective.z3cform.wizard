import doctest
import unittest

from zope.component import testing, provideAdapter
import z3c.form.testing
import plone.z3cform.tests
from z3c.form.datamanager import DictionaryField

def setUp(test):
    testing.setUp(test)
    z3c.form.testing.setupFormDefaults()
    plone.z3cform.tests.setup_defaults()
    provideAdapter(DictionaryField)

class MockSession(dict):
    def set(self, key, value):
        self[key] = value

class TestRequest(z3c.form.testing.TestRequest):
    
    def __init__(self, **kw):
        z3c.form.testing.TestRequest.__init__(self, **kw)
        self.SESSION = MockSession()

def test_suite():
    return unittest.TestSuite([

        doctest.DocFileSuite(
            'wizard.txt',
            setUp=setUp,
            tearDown=testing.tearDown,
            optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            globs=globals(),
            )

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
