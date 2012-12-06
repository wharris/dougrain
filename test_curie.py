#!/usr/bin/python
import unittest
import curie

class CurieTest(unittest.TestCase):
    def setUp(self):
        self.curies = curie.CurieCollection("http://localhost/api/prodcuts/1")
        self.curies['role'] = "http://localhost/roles/"
        self.curies['spec'] = "/specifications/"

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

