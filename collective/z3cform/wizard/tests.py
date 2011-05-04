import doctest
import unittest

from zope.testing.doctest import DocFileSuite
from zope.component import testing, provideAdapter
from zope.configuration import xmlconfig
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable
import z3c.form.testing
import plone.z3cform.tests
import Products.statusmessages
import zope.component
import zope.app.component
import zope.app.security
import zope.i18n
import z3c.form
from z3c.form.datamanager import DictionaryField

def setUp(test):
    testing.setUp(test)
    z3c.form.testing.setupFormDefaults()
    plone.z3cform.tests.setup_defaults()
    provideAdapter(DictionaryField)
    xmlconfig.XMLConfig('meta.zcml', zope.component)()
    xmlconfig.XMLConfig('meta.zcml', zope.app.component)()
    xmlconfig.XMLConfig('meta.zcml', zope.app.security)()
    xmlconfig.XMLConfig('meta.zcml', zope.i18n)()
    xmlconfig.XMLConfig('meta.zcml', z3c.form)()
    xmlconfig.XMLConfig('configure.zcml', zope.app.security)()
    xmlconfig.XMLConfig('configure.zcml', z3c.form)()
    xmlconfig.XMLConfig('configure.zcml', Products.statusmessages)()

class MockSession(dict):
    def set(self, key, value):
        self[key] = value

class TestRequest(z3c.form.testing.TestRequest):
    implements(IAttributeAnnotatable)

    def __init__(self, **kw):
        z3c.form.testing.TestRequest.__init__(self, **kw)
        self.SESSION = MockSession()

def test_suite():
    return unittest.TestSuite([

        DocFileSuite(
            'wizard.txt',
            setUp=setUp,
            tearDown=testing.tearDown,
            optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            globs=globals(),
            )

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
