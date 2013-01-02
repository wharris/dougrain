#!/usr/bin/python
import unittest
from dougrain import curie
from dougrain import link

class CurieTest(unittest.TestCase):
    def setUp(self):
        self.curies = curie.CurieCollection()
        tlink = lambda url: link.Link(dict(href=url, templated=True),
                                      "http://localhost/api/products/1")
        self.curies['role'] = tlink("http://localhost/roles/{relation}")
        self.curies['spec'] = tlink("/specifications/{relation}")

    def testExpandsAbsoluteCurie(self):
        self.assertEquals("http://localhost/roles/host",
                          self.curies.expand("role:host"))

    def testExpandsRelativeCurie(self):
        self.assertEquals("http://localhost/specifications/color",
                          self.curies.expand("spec:color"))

    def testNullExpandsAbsoluteUrl(self):
        self.assertEquals("http://localhost/tags/foo",
                          self.curies.expand("http://localhost/tags/foo"))

    def testNullExpandsLinkWithUnknownCurieName(self):
        self.assertEquals("unknowncurie:foo",
                          self.curies.expand("unknowncurie:foo"))

    def testNullExpandsLinkWithNoCurieName(self):
        self.assertEquals("next", self.curies.expand("next"))

if __name__ == '__main__':
    unittest.main()

