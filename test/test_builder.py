#!/usr/bin/python
# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import unittest
from dougrain import Builder, Document, drafts

class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.uri = "http://localhost/%s/%s" % (self.__class__.__name__,
                                               self._testMethodName)
        self.builder = Builder(self.uri)


class PropertyBuilderTests(BuilderTests):
    def testStartsWithNoProperties(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.properties.keys(), [])

    def testSetNewProperty(self):
        self.builder.set_property('spam', "foo")

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")

        self.assertEquals(doc.properties['spam'], "foo")


class LinkBuilderTests(BuilderTests):
    def testAlreadyHasSelfLink(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('self', doc.links)
        
        self_link = doc.links['self']
        self.assertEqual(self_link.url(), self.uri)
        self.assertEqual(doc.url(), self.uri)
        self.assertEqual(doc.links.keys(), ['self'])

    def testAddSimpleLink(self):
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

    def testAddWrappedLink(self):
        self.builder.add_link('item', '/items/1', wrap=True)
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('item', doc.links)
        
        item_link = doc.links['item']
        self.assertEqual(item_link.url(), doc.link("/items/1").url())

    def testAddSecondWrappedLink(self):
        self.builder.add_link('item', '/items/1', name='first', wrap=True)
        self.builder.add_link('item', '/items/2', name='second', wrap=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second'])

    def testFirstUnwrappedLinkIsDict(self):
        self.builder.add_link('item', '/items/1', wrap=False)
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testFirstWrappedLinkIsList(self):
        self.builder.add_link('item', '/items/1', wrap=True)
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              list)

    def testDefaultLinkIsNotWrapped(self):
        self.builder.add_link('item', '/items/1')
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testStartsWithNoCuries(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertSequenceEqual(doc.curies.keys(), [])

        self.assertEqual(doc.expand_curie('rel:spam'), "rel:spam")


class CurieBuilderTests(BuilderTests):
    def testAddCurie(self):
        self.builder.add_curie('rel', "/rels/{rel}")
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.expand_curie('rel:spam'),
                         "http://localhost/rels/spam")

    def testAddSecondCurie(self):
        self.builder.add_curie('rel', "/rels/{rel}")
        self.builder.add_curie('admin', "/rels/admin/{rel}")
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.expand_curie('rel:spam'),
                         "http://localhost/rels/spam")
        self.assertEqual(doc.expand_curie('admin:eggs'),
                         "http://localhost/rels/admin/eggs")

    def testAddCurieDraft5(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_5)
        self.builder.add_curie('rel', "/rels/{rel}")
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost",
                                   draft=drafts.DRAFT_5)
        self.assertEqual(doc.expand_curie('rel:spam'),
                         "http://localhost/rels/spam")

        curies = self.builder.as_object()['_links']['curies']
        self.assertIsInstance(curies, list)

    def testAddCurieDraft4(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_4)
        self.builder.add_curie('rel', "/rels/{rel}")
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost",
                                   draft=drafts.DRAFT_4)
        self.assertEqual(doc.expand_curie('rel:spam'),
                         "http://localhost/rels/spam")

        curies = self.builder.as_object()['_links']['curies']
        self.assertIsInstance(curies, list)

    def testAddCurieDraft3(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_3)
        self.builder.add_curie('rel', "/rels/{rel}")
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost",
                                   draft=drafts.DRAFT_3)
        self.assertEqual(doc.expand_curie('rel:spam'),
                         "http://localhost/rels/spam")

        curies = self.builder.as_object()['_links']['curie']
        self.assertIsInstance(curies, dict)


class EmbedBuilderTests(BuilderTests):
    def make_target(self, name):
        target_uri = "http://localhost/%s/%s/%s" % (self.__class__.__name__,
                                                    self._testMethodName,
                                                    name)
        target_builder = Builder(target_uri)
        target_builder.set_property('name', name)
        return target_builder

    def testFirstEmbedDefault(self):
        target = self.make_target("first")
        self.builder.embed('item', target)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_embedded']['item'],
                              dict)
        self.assertEquals(doc.embedded['item'].properties['name'], "first")

    def testFirstEmbedNotWrapped(self):
        target = self.make_target("first")
        self.builder.embed('item', target, wrap=False)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_embedded']['item'],
                              dict)
        self.assertEquals(doc.embedded['item'].properties['name'], "first")

    def testFirstEmbedWrapped(self):
        target = self.make_target("first")
        self.builder.embed('item', target, wrap=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_embedded']['item'],
                              list)
        item_embeds = doc.embedded['item']
        names = [embedded.properties['name'] for embedded in item_embeds]
        self.assertEquals(names, ["first"])

    def testSecondEmbed(self):
        self.builder.embed('item', self.make_target('first'))
        self.builder.embed('item', self.make_target('second'))

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_embeds = doc.embedded['item']
        names = [embedded.properties['name'] for embedded in item_embeds]
        self.assertSequenceEqual(names, ['first', 'second'])

    def testThirdEmbed(self):
        self.builder.embed('item', self.make_target('first'))
        self.builder.embed('item', self.make_target('second'))
        self.builder.embed('item', self.make_target('third'))

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_embeds = doc.embedded['item']
        names = [embedded.properties['name'] for embedded in item_embeds]
        self.assertSequenceEqual(names, ['first', 'second', 'third'])

    def testThreeWrappedEmbeds(self):
        self.builder.embed('item', self.make_target('first'), wrap=True)
        self.builder.embed('item', self.make_target('second'), wrap=True)
        self.builder.embed('item', self.make_target('third'), wrap=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_embeds = doc.embedded['item']
        names = [embedded.properties['name'] for embedded in item_embeds]
        self.assertSequenceEqual(names, ['first', 'second', 'third'])


class EmbedBuilderDocumentTests(EmbedBuilderTests):
    def make_target(self, name):
        target_uri = "http://localhost/%s/%s/%s" % (self.__class__.__name__,
                                                    self._testMethodName,
                                                    name)
        target_doc = Document.empty("http://localhost")
        target_doc.add_link('self', target_uri)
        target_doc.set_property('name', name)
        return target_doc



if __name__ == '__main__':
    unittest.main()
