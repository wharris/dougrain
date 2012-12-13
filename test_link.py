#!/usr/bin/python
import unittest
import link

class TestParseAbsoluteLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {'href': "http://localhost/"},
            None)

    def testLoadsAbsoluteHref(self):
        self.assertEquals("http://localhost/", self.link.href)

    def testCalculatesUrl(self):
        self.assertEquals("http://localhost/", self.link.url())

    def testNameIsMissing(self):
        self.assertFalse(hasattr(self.link, 'name'))

    def testLabelIsMissing(self):
        self.assertFalse(hasattr(self.link, 'label'))


class TestParseRelativeLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {'href': "/foo"},
            "http://localhost/")

    def testLoadsAbsoluteHref(self):
        self.assertEquals("/foo", self.link.href)

    def testCalculatesUrl(self):
        self.assertEquals("http://localhost/foo", self.link.url())

    def testNameIsMissing(self):
        self.assertFalse(hasattr(self.link, 'name'))

    def testLabelIsMissing(self):
        self.assertFalse(hasattr(self.link, 'label'))


class TestParseAdditionalAttributes(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo",
                'name': "bar",
                'label': "Bar"
            },
            "http://localhost/"
        )

    def testLoadsName(self):
        self.assertEquals("bar", self.link.name)

    def testLoadsLabel(self):
        self.assertEquals("Bar", self.link.label)


class TestExpandTemplatedLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo/{arg1}",
                'templated': True
            },
            "http://localhost/"
        )

    def testHasArgs(self):
        self.assertEquals(["arg1"], self.link.variables)

    def testSubstituteNoArgs(self):
        self.assertEquals("http://localhost/foo/", self.link.url())

    def testSubstituteArg(self):
        self.assertEquals("http://localhost/foo/1-bar",
                          self.link.url(arg1="1-bar"))

    def testPreservesTemplate(self):
        self.assertEquals("http://localhost/foo/{arg1}", self.link.template)


if __name__ == '__main__':
    unittest.main()
