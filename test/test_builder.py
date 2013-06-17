#!/usr/bin/python
# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import unittest
from dougrain import Builder, Document

class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.uri = "http://localhost/%s/%s" % (self.__class__.__name__,
                                               self._testMethodName)
        self.builder = Builder(self.uri)

    def testSetNewProperty(self):
        self.builder.set_property('spam', "foo")

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")

        self.assertEquals(doc.properties['spam'], "foo")

    def testAlreadyHasSelfLink(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('self', doc.links)
        
        self_link = doc.links['self']
        self.assertEqual(self_link.url(), self.uri)
        self.assertEqual(doc.url(), self.uri)

    def testAddSimpleLink(self):
        before = Document.from_object(self.builder.as_object(),
                                      base_uri="http://localhost")
        self.assertNotIn('item', before.links)

        self.builder.add_link('item', "/items/1")

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('item', doc.links)
        
        item_link = doc.links['item']
        self.assertEqual(item_link.url(), doc.link("/items/1").url())


if __name__ == '__main__':
    unittest.main()
