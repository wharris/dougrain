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

    def testStartsWithNoProperties(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.properties.keys(), [])

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

    def testAddLinkWithOptionalProperties(self):
        self.builder.add_link('item', "/items/{item_id}",
                              name='name',
                              title='Title',
                              type='application/hal+json',
                              profile='/profiles/item',
                              hreflang='en',
                              deprecation='/deprecation/item',
                              templated=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_link = doc.links['item']
        self.assertEqual(item_link.url(item_id='1'), "http://localhost/items/1")
        self.assertEqual(item_link.name, 'name')
        self.assertEqual(item_link.title, 'Title')
        self.assertEqual(item_link.type, 'application/hal+json')
        self.assertEqual(item_link.profile, '/profiles/item')
        self.assertEqual(item_link.hreflang, 'en')
        self.assertEqual(item_link.deprecation, '/deprecation/item')
        self.assertTrue(item_link.is_templated)

    def testAddSecondLink(self):
        self.builder.add_link('item', '/items/1', name='first')
        self.builder.add_link('item', '/items/2', name='second')

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second'])

    def testAddThirdLink(self):
        self.builder.add_link('item', '/items/1', name='first')
        self.builder.add_link('item', '/items/2', name='second')
        self.builder.add_link('item', '/items/3', name='third')

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second', 'third'])


if __name__ == '__main__':
    unittest.main()
