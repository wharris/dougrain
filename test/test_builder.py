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


class InitialBuilderTests(BuilderTests):
    def testStartsWithNoProperties(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.properties.keys(), [])

    def testAlreadyHasSelfLink(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('self', doc.links)
        
        self_link = doc.links['self']
        self.assertEqual(self_link.url(), self.uri)
        self.assertEqual(doc.url(), self.uri)
        self.assertEqual(doc.links.keys(), ['self'])

    def testStartsWithNoEmbeds(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertEqual(doc.embedded.keys(), [])
        

class PropertyBuilderTests(BuilderTests):
    def testSetNewProperty(self):
        self.builder.set_property('spam', "foo")

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")

        self.assertEquals(doc.properties['spam'], "foo")


class LinkBuilderTestsMixin(object):
    def make_target(self, href):
        raise NotImplemented

    def add_link(self, rel, href, **kwargs):
        self.builder.add_link(rel, self.make_target(href), **kwargs)

    def testAddSimpleLink(self):
        self.add_link('item', "/items/1")

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('item', doc.links)
        
        item_link = doc.links['item']
        self.assertEqual(item_link.url(), doc.link("/items/1").url())

    def testAddLinkWithOptionalProperties(self):
        self.add_link('item', "/items/{item_id}",
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
        self.add_link('item', '/items/1', name='first')
        self.add_link('item', '/items/2', name='second')

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second'])

    def testAddThirdLink(self):
        self.add_link('item', '/items/1', name='first')
        self.add_link('item', '/items/2', name='second')
        self.add_link('item', '/items/3', name='third')

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second', 'third'])

    def testAddWrappedLink(self):
        self.add_link('item', '/items/1', wrap=True)
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIn('item', doc.links)
        
        item_link = doc.links['item']
        self.assertEqual(item_link.url(), doc.link("/items/1").url())

    def testAddSecondWrappedLink(self):
        self.add_link('item', '/items/1', name='first', wrap=True)
        self.add_link('item', '/items/2', name='second', wrap=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        self.assertSequenceEqual([item_link.name for item_link in item_links],
                                 ['first', 'second'])

    def testFirstUnwrappedLinkIsDict(self):
        self.add_link('item', '/items/1', wrap=False)
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testFirstWrappedLinkIsList(self):
        self.add_link('item', '/items/1', wrap=True)
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              list)

    def testDefaultLinkIsNotWrapped(self):
        self.add_link('item', '/items/1')
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testStartsWithNoCuries(self):
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertSequenceEqual(doc.curies.keys(), [])

        self.assertEqual(doc.expand_curie('rel:spam'), "rel:spam")


class HrefLinkBuilderTests(BuilderTests, LinkBuilderTestsMixin):
    def make_target(self, href):
        return href


class UnicodeHrefLinkBuilderTests(BuilderTests, LinkBuilderTestsMixin):
    def make_target(self, href):
        return unicode(href)


class BuilderLinkBuilderTests(BuilderTests, LinkBuilderTestsMixin):
    def make_target(self, href):
        return Builder(href)


class DocumentLinkBuilderTests(BuilderTests, LinkBuilderTestsMixin):
    def make_target(self, href):
        doc = Document.empty("http://localhost/")
        doc.add_link('self', href)
        return doc


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

    def testEmbedAlsoAddsLinkWithDraft5(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_5)
        self.builder.embed('item', self.make_target('first'))
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links['item']
        urls = [link.url() for link in item_links]
        item_embeds = doc.embedded['item']
        expected_urls = [embedded.url() for embedded in item_embeds]
        self.assertSequenceEqual(urls, expected_urls)

    def testEmbedDoesNotAddLinkWithDraft4(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_4)
        self.builder.embed('item', self.make_target('first'))
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links.get('item', [])
        urls = [link.url() for link in item_links]
        item_embeds = doc.embedded['item']
        expected_urls = []
        self.assertSequenceEqual(urls, expected_urls)

    def testEmbedDoesNotAddLinkWithDraft3(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_3)
        self.builder.embed('item', self.make_target('first'))
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        item_links = doc.links.get('item', [])
        urls = [link.url() for link in item_links]
        item_embeds = doc.embedded['item']
        expected_urls = []
        self.assertSequenceEqual(urls, expected_urls)

    def testEmbedAddsUnnecessaryLinkWithDraft5(self):
        self.builder = Builder(self.uri, draft=drafts.DRAFT_5)
        target = self.make_target('first')

        self.builder.add_link('item', target, wrap=True)
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        urls_before_embed = [link.url() for link in doc.links['item']]

        self.builder.embed('item', target, wrap=True)
        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        urls_after_embed = [link.url() for link in doc.links['item']]

        item_embeds = doc.embedded['item']
        embedded_urls = [embedded.url() for embedded in item_embeds]
        expected_urls = urls_before_embed + embedded_urls
        self.assertSequenceEqual(urls_after_embed, expected_urls)

    def testAutomaticLinkIsNotWrappedDefault(self):
        target = self.make_target("first")
        self.builder.embed('item', target)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testAutomaticLinkIsNotWrappedWithUnwrappedEmbed(self):
        target = self.make_target("first")
        self.builder.embed('item', target, wrap=False)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              dict)

    def testAutomaticLinkIsWrappedWithWrappedEmbed(self):
        target = self.make_target("first")
        self.builder.embed('item', target, wrap=True)

        doc = Document.from_object(self.builder.as_object(),
                                   base_uri="http://localhost")
        self.assertIsInstance(self.builder.as_object()['_links']['item'],
                              list)


class EmbedBuilderDocumentTests(EmbedBuilderTests):
    def make_target(self, name):
        target_uri = "http://localhost/%s/%s/%s" % (self.__class__.__name__,
                                                    self._testMethodName,
                                                    name)
        target_doc = Document.empty("http://localhost")
        target_doc.add_link('self', target_uri)
        target_doc.set_property('name', name)
        return target_doc


class ChainingBuilderTests(unittest.TestCase):
    def testChainAfterSetProperty(self):
        obj = (Builder("/item/1")
               .set_property("name", "Thing #1")
               .set_property("chained", True)).as_object()

        doc = Document.from_object(obj, base_uri="http://localhost/")

        self.assertTrue(doc.properties['chained'])
        
    def testChainAfterAddLink(self):
        obj = (Builder("/item/1")
               .add_link("next", "/item/2")
               .set_property("chained", True)).as_object()

        doc = Document.from_object(obj, base_uri="http://localhost/")

        self.assertTrue(doc.properties['chained'])
        
    def testChainAfterAddCurie(self):
        obj = (Builder("/item/1")
               .add_curie("rel", "/rels/{rel}")
               .set_property("chained", True)).as_object()

        doc = Document.from_object(obj, base_uri="http://localhost/")

        self.assertTrue(doc.properties['chained'])

    def testChainAfterEmbed(self):
        target = Builder("/item/2")
        obj = (Builder("/item/1")
               .embed("next", target)
               .set_property("chained", True)).as_object()

        doc = Document.from_object(obj, base_uri="http://localhost/")

        self.assertTrue(doc.properties['chained'])

    def testBuildDocument(self):
        obj = (Builder("/products/254-rocket-skates")
               .add_curie('api', '/rels/{rel}')
               .set_property('name', "Rocket Skates")
               .set_property(
                   'description',
                   "Endorsed by top athletes, these affordable ...")
               .set_property('ean', "55-5555-5555-X")
               .add_link('api:reviews', "/products/254-rocket-skates/reviews")
               .embed('api:pictures',
                      Builder("/products/254-rocket-skates/pictures/")
                      .set_property('count', 2)
                      .add_link('item',
                                "/products/254-rocket-skates/pictures/1")
                      .add_link('item',
                                "/products/254-rocket-skates/pictures/2")
                      .embed('item',
                             Builder("/products/254-rocket-skates/pictures/1")
                             .set_property('count', 1)
                             .add_link('api:subject',
                                       "/products/254-rocket-skates")
                             .add_link('item', "/images/48184234")
                             .embed('item',
                                    Builder("/images/48184234")
                                    .set_property('width', 2048)
                                    .set_property('height', 1536)
                                    .add_link(
                                        'enclosure',
                                        "http://images.localhost/48184234.png",
                                        type="image/jpeg"))))
               .add_link('api:pictures',
                         "/products/254-rocket-skates/pictures/")
               .add_link('api:price', "/prices/537461",
                     title="$24.95 + $1.00 delivery")
               .embed('api:price',
                      Builder("/prices/537461")
                      .set_property("currency_code", "USD")
                      .set_property("currency_symbol", "$")
                      .set_property("advertised_price", "24.95")
                      .set_property("delivery_price", "1.00")
                      .set_property("total_price", "25.95"))
              ).as_object()

        doc = Document.from_object(obj, base_uri="http://localhost/")
        self.assertEqual(doc.properties['name'], "Rocket Skates")
        self.assertEqual(doc.links['/rels/reviews'].url(),
                         "http://localhost/products/254-rocket-skates/reviews")
        item = doc.embedded['/rels/pictures'].embedded['item'].embedded['item']
        self.assertEquals(item.properties['width'], 2048)
        self.assertEquals(item.links['enclosure'].type, "image/jpeg")


if __name__ == '__main__':
    unittest.main()
