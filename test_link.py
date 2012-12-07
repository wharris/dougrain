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
        self.assertEquals("http://localhost/", self.link.url)

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
        self.assertEquals("http://localhost/foo", self.link.url)

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


if __name__ == '__main__':
    unittest.main()
