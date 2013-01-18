#!/usr/bin/python
# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import unittest
import dougrain

class ParseSimpleTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.from_object({"name": "David Bowman"})

    def testParseSimple(self):
        self.assertEquals(self.doc.attrs['name'], "David Bowman")

    def testHasEmptyLinks(self):
        self.assertEquals(self.doc.links, {})


class ParseLinksTest(unittest.TestCase):
    OBJECT = {
        "_links": {
            "self": {"href": "dougrain"},
            "next": {
                "href": "http://localhost/wharris/esmre",
                "label": "Next"
            },
            "parent": {"href": "/wharris/"},
            "images": [
                {"href": "/foo"},
                {"href": "/bar"}
            ],
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(
            self.OBJECT, relative_to_url="http://localhost/wharris/dougrain")

    def testLoadsSingleLinkHref(self):
        self.assertEquals("http://localhost/wharris/esmre",
                          self.doc.links["next"].href)

    def testLoadsSingleLinkURL(self):
        self.assertEquals("http://localhost/wharris/esmre",
                          self.doc.links["next"].url())

    def testLoadsRelativeURLHref(self):
        self.assertEquals("/wharris/",
                          self.doc.links["parent"].href)

    def testAbsolutesRelativeURL(self):
        self.assertEquals("http://localhost/wharris/",
                          self.doc.links["parent"].url())

    def testLoadsSelfAsLinkAndAttribute(self):
        self.assertEquals("dougrain", self.doc.links["self"].href)
        self.assertEquals("http://localhost/wharris/dougrain",
                          self.doc.links["self"].url())

        self.assertEquals(self.doc.links["self"].url(), self.doc.url())

    def testLoadsLabel(self):
        self.assertEquals("Next", self.doc.links["next"].label)
        self.assertFalse(hasattr(self.doc.links["parent"], "label"))
        self.assertFalse(hasattr(self.doc.links["self"], "label"))

    def testLoadsArrayOfLinks(self):
        self.assertEquals(["/foo", "/bar"],
                          [link.href for link in self.doc.links['images']])

    def testLinksIsNotAnAttribute(self):
        self.assertFalse('_links' in self.doc.attrs)
        self.assertFalse(hasattr(self.doc, '_links'))


class ParseEmbeddedObjectsTest(unittest.TestCase):
    OBJECT = {
        "_embedded": {
            "foo": {
                "name": "Foo",
                "size": 88888888
            },
            "bar": [
                {
                    "title": "Bar 1"
                },
                {
                    "title": "Bar 2"
                }
            ],
            "bundy": {
                "_links": {
                    "next": {"href": "/people/2"}
                }
            }
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(
            self.OBJECT,
            relative_to_url="http://localhost/people/")

    def testLoadsSingleEmbeddedObject(self):
        foo = self.doc.embedded["foo"]
        self.assertEquals("Foo", foo.attrs['name'])
        self.assertEquals(88888888, foo.attrs['size'])

    def testLoadsArrayOfEmbeddedObjects(self):
        self.assertEquals(["Bar 1", "Bar 2"],
                          [bar.attrs['title']
                           for bar in self.doc.embedded['bar']])

    def testLoadsLinksInEmbeddedObject(self):
        link = self.doc.embedded["bundy"].links["next"]
        self.assertEquals("/people/2", link.href)
        self.assertEquals("http://localhost/people/2", link.url())

    def testEmbeddedIsNotAnAttribute(self):
        self.assertFalse('_embedded' in self.doc.attrs)
        self.assertFalse(hasattr(self.doc, '_embedded'))


class CurieExpansionTest(unittest.TestCase):
    OBJECT = {
        '_links': {
            'curie': [
                {
                    'href': "http://localhost/roles/{relation}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{relation}",
                    'name': 'image'
                }
            ],
            'role:host': {'href': "/hosts/1"}
        },
        '_embedded': {
            'role:sizing': {
                '_links': {
                    'curie': [
                        {
                            'href':
                            "http://localhost/dimension/{relation}",
                            'name': 'dim',
                            'templated': True
                        }
                    ]
                }
            },
            'role:coloring': {
                '_links': {
                    'curie': [
                        {
                            'href':
                            "http://localhost/imagefiles/{relation}",
                            'name': 'image',
                            'templated': True
                        }
                    ]
                }
            },
        }
    }

    def setUp(self):
        self.doc = dougrain.Document.from_object(self.OBJECT)

    def testExposesCurieCollection(self):
        self.assertEquals("http://localhost/roles/category",
                          self.doc.expand_curie('role:category'))

    def testEmbeddedObjectHasParentCuries(self):
        sizing_doc = self.doc.embedded['role:sizing']
        self.assertEquals("http://localhost/roles/host",
                          sizing_doc.expand_curie('role:host'))

    def testParentObjectDoesNotHaveEmbeddedCuried(self):
        self.assertEquals('dim:weight', self.doc.expand_curie('dim:weight'))

    def testEmbeddedObjectExtendsParentCuries(self):
        sizing_doc = self.doc.embedded['role:sizing']
        self.assertEquals("http://localhost/dimension/weight",
                          sizing_doc.expand_curie('dim:weight'))

    def testEmbeddedObjectCurieOverridesParentCurie(self):
        coloring_doc = self.doc.embedded['role:coloring']
        self.assertEquals("http://localhost/imagefiles/photo",
                          coloring_doc.expand_curie('image:photo'))


class RelsTest(unittest.TestCase):
    OBJECT = {
        '_links': {
            'curie': [
                {
                    'href': "/roles/{relation}",
                    'name': 'role',
                    'templated': True
                },
                {
                    'href': "http://localhost/images/{relation}",
                    'name': 'image',
                    'templated': True
                }
            ],
            'role:host': {'href': "/hosts/1"},
            'role:application': {'href': "/apps/1"},
            'role:dept': [
                {'href': "/departments/1"},
                {'href': "/departments/2"}
            ]
        },
        '_embedded': {
            'role:consumer': {
                '_links': {
                    'self': {
                        'href': '/clients/1'
                    }
                },
                'name': "Client 1"
            },
            'role:application': {
                '_links': {
                    'self': { 'href': "/apps/2" }
                }
            },
            'role:dept': [
                {
                    '_links': {
                        'self': {
                            'href': "http://localhost/departments/2"
                        }
                    },
                },
                {
                    '_links': {
                        'self': { 'href': "/departments/3" }
                    }
                }
            ]
        }
    }
    
    def setUp(self):
        self.doc = dougrain.Document(self.OBJECT, "http://localhost")

    def testHasHostLinkRel(self):
        host_role = self.doc.expand_curie('role:host')
        self.assertTrue(host_role in self.doc.rels)
        self.assertEquals(["http://localhost/hosts/1"],
                          [x.url() for x in self.doc.rels[host_role]])

    def testHasConsumerEmbeddedRel(self):
        consumer_role = self.doc.expand_curie('role:consumer')
        self.assertTrue(consumer_role in self.doc.rels)
        consumer = self.doc.rels[consumer_role][0]
        self.assertEquals("http://localhost/clients/1", consumer.url())
        self.assertEquals("Client 1", consumer.attrs['name'])

    def testHasApplicationLinkAndEmbeddedRels(self):
        application_role = self.doc.expand_curie('role:application')
        applications = self.doc.rels[application_role]
        self.assertTrue(self.doc.embedded['role:application'] in applications)
        self.assertTrue(self.doc.links['role:application'] in applications)

    def testEmbeddedRelOverridesLinkRelWithSameHref(self):
        dept_role = self.doc.expand_curie('role:dept')

        dept_2_link = [link for link in self.doc.links['role:dept']
                       if link.url() == "http://localhost/departments/2"][0]
        dept_2_embedded = [link for link in self.doc.embedded['role:dept']
                           if link.url() == "http://localhost/departments/2"][0]
        
        departments = self.doc.rels[dept_role]
        self.assertTrue(dept_2_embedded in departments)
        self.assertFalse(dept_2_link in departments)

        urls = [x.url() for x in departments]
        urls.sort()
        self.assertEquals(
            ["http://localhost/departments/%d" % x for x in [1,2,3]],
            urls)


class SerializeTests(unittest.TestCase):
    def checkEqualObjects(self, obj):
        doc = dougrain.Document.from_object(obj, "http://localhost")
        self.assertEquals(obj, doc.as_object())

    def testSimple(self):
        self.checkEqualObjects({})

    def testAttributes(self):
        self.checkEqualObjects({"latlng": [53.0, -0.001],
                                "altitude": 10.0,
                                "haccuracy": 5.0,
                                "vacuracy": 10.0})

    def testLinks(self):
        self.checkEqualObjects(ParseLinksTest.OBJECT)

    def testEmbeddedObjects(self):
        self.checkEqualObjects(ParseEmbeddedObjectsTest.OBJECT)

    def testRels(self):
        self.checkEqualObjects(CurieExpansionTest.OBJECT)
        self.checkEqualObjects(RelsTest.OBJECT)


class AttributeMutationTests(unittest.TestCase):
    def testSetAttributeAddsAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_attribute('foo', "bar")

        self.assertEquals("bar", doc.attrs['foo'])

    def testSetAttributeUpdatesAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_attribute('foo', "bar")

        doc.set_attribute('foo', "bundy")

        self.assertEquals("bundy", doc.attrs['foo'])

    def testRemoveAttributeRemovesAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_attribute('foo', "bar")

        doc.delete_attribute('foo')

        self.assertFalse(hasattr(doc, 'foo'))
        self.assertFalse('foo' in doc.attrs)

    def testBuildObjectFromEmpty(self):
        target = {"latlng": [53.0, -0.001],
                  "altitude": 10.0,
                  "haccuracy": 5.0,
                  "vacuracy": 10.0}
        target_doc = dougrain.Document.from_object(target)

        doc = dougrain.Document.empty()

        for key, value in target_doc.attrs.iteritems():
            doc.set_attribute(key, value)

        self.assertEquals(target_doc.as_object(), doc.as_object())


class AddLinkStringTests(unittest.TestCase):
    def add_link(self, doc, rel, href, **kwargs):
        doc.add_link(rel, href, **kwargs)

    def testAddSimpleLink(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/1"}
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/1")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddLinkForSecondRelKeepsFirstRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/1"},
                'child': {'href': "http://localhost/1/1"}
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/1")
        self.add_link(doc, 'child', "http://localhost/1/1")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddSecondLinkForSameRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1"},
                          {'href': "http://localhost/2/2"}]
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1")
        self.add_link(doc, 'child', "http://localhost/2/2")

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddThirdLinkForSameRel(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1"},
                          {'href': "http://localhost/2/2"},
                          {'href': "http://localhost/2/3"}]
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1")
        self.add_link(doc, 'child', "http://localhost/2/2")
        self.add_link(doc, 'child', "http://localhost/2/3")

        self.assertEquals(target, doc.as_object())

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)

    def testAddLinkWithExtraAttributes(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [{'href': "http://localhost/2/1",
                           'label': "First Child"},
                          {'href': "http://localhost/2/2",
                           'label': "Second Child"}]
            }
        }
        doc = dougrain.Document.empty()
        self.add_link(doc, 'self', "http://localhost/2")
        self.add_link(doc, 'child', "http://localhost/2/1", label="First Child")
        self.add_link(doc, 'child', "http://localhost/2/2", label="Second Child")

        self.assertEquals(target, doc.as_object())


class AddObjectLinkTests(AddLinkStringTests):
    def add_link(self, doc, rel, href, **kwargs):
        link = doc.link(href, **kwargs)
        doc.add_link(rel, link)


class DeleteLinkTests(unittest.TestCase):
    def testDeleteOnlyLinkForRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': {'href': "http://localhost/2/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/2"},
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")

        self.assertEquals(target_doc, doc)
        self.assertFalse('child' in doc.links)

    def testDeleteEveryLinkForRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [
                    {'href': "http://localhost/2/1"},
                    {'href': "http://localhost/2/2"},
                    {'href': "http://localhost/2/3"}
                ]
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/2"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.links)


    def testDeleteLastLink(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': {'href': "http://localhost/2/1"}
            }
        }

        target = {}

        doc = dougrain.Document.from_object(initial, "http://localhost/")
        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc.delete_link("child")
        doc.delete_link("self")

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteIndividualLinks(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/2"},
                'child': [
                    {'href': "http://localhost/2/1"},
                    {'href': "http://localhost/2/2"},
                    {'href': "http://localhost/2/3"}
                ]
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link("child", "http://localhost/2/1")
        self.assertEquals([{'href': "http://localhost/2/2"},
                           {'href': "http://localhost/2/3"}],
                          doc.as_object()['_links']['child'])

        doc.delete_link("child", "http://localhost/2/3")
        self.assertEquals({'href': "http://localhost/2/2"},
                          doc.as_object()['_links']['child'])
        
        doc.delete_link("child", "http://localhost/2/2")
        self.assertFalse("child" in doc.as_object()['_links'])

        doc.delete_link("self", "http://localhost/2")
        self.assertFalse('_links' in doc.as_object())

    def testDeleteLinksWithoutRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': {'href': "http://localhost/3/2"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link(href="http://localhost/3/1")

        self.assertEquals(target, doc.as_object())

    def testDeleteAllLinks(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {}

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link()

        self.assertEquals(target, doc.as_object())

    def testDeleteLinkWithNoMatchingRel(self):
        initial = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        target = {
            '_links': {
                'self': {'href': "http://localhost/3"},
                'child': [{'href': "http://localhost/3/1"},
                          {'href': "http://localhost/3/2"}],
                'favorite': {'href': "http://localhost/3/1"}
            }
        }

        doc = dougrain.Document.from_object(initial, "http://localhost/")

        doc.delete_link(rel="".join(doc.links.keys()))

        self.assertEquals(target, doc.as_object())

    def testDeleteLinkWithNoLinks(self):
        doc = dougrain.Document.empty("http://localhost/3")
        target = dougrain.Document.empty("http://localhost/3")

        doc.delete_link()

        self.assertEquals(target, doc)


class EmbedTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.empty("http://localhost/")
        self.embedded1 = dougrain.Document.from_object({"foo": "bar"})
        self.embedded2 = dougrain.Document.from_object({"spam": "eggs"})
        self.embedded3 = dougrain.Document.from_object({"ham": "beans"})

    def testEmbed(self):
        expected = {
            '_embedded': {
                'child': self.embedded1.as_object()
            }
        }
        self.doc.embed('child', self.embedded1)
        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals(self.embedded1, self.doc.embedded['child'])

    def testEmbedAnotherRel(self):
        expected = {
            '_embedded': {
                'prev': self.embedded2.as_object(),
                'next': self.embedded3.as_object(),
            }
        }
        self.doc.embed('prev', self.embedded2)
        self.doc.embed('next', self.embedded3)

        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals(self.embedded2, self.doc.embedded['prev'])
        self.assertEquals(self.embedded3, self.doc.embedded['next'])

    def testEmbedSameRel(self):
        expected = {
            '_embedded': {
                'item': [
                    self.embedded1.as_object(),
                    self.embedded2.as_object(),
                    self.embedded3.as_object()
                ]
            }
        }
        self.doc.embed('item', self.embedded1)
        self.doc.embed('item', self.embedded2)
        self.doc.embed('item', self.embedded3)

        self.assertEquals(expected, self.doc.as_object())
        self.assertEquals([self.embedded1, self.embedded2, self.embedded3],
                          self.doc.embedded['item'])


def make_doc(href):
    result = dougrain.Document.empty("http://localhost")
    result.add_link('self', href)
    return result


class DeleteEmbeddedTests(unittest.TestCase):
    def doc(self, href):
        return make_doc(href)

    def testDeleteOnlyEmbedForRel(self):
        doc = self.doc("http://localhost/2")
        doc.embed('child', self.doc("http://localhost/2/1"))
        doc.embed('root', self.doc("http://localhost/"))

        target_doc = self.doc("http://localhost/2")
        target_doc.embed('root', self.doc("http://localhost/"))

        doc.delete_embedded("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.embedded)
        self.assertTrue('root' in doc.embedded)

    def testDeleteEveryEmbedForRel(self):
        doc = self.doc("http://localhost/2")
        doc.embed('root', self.doc("http://localhost/"))
        doc.embed('child', self.doc("http://localhost/2/1"))
        doc.embed('child', self.doc("http://localhost/2/1"))
        doc.embed('child', self.doc("http://localhost/2/1"))

        target_doc = self.doc("http://localhost/2")
        target_doc.embed('root', self.doc("http://localhost/"))

        doc.delete_embedded("child")

        self.assertEquals(target_doc.as_object(), doc.as_object())
        self.assertFalse('child' in doc.embedded)
        self.assertTrue('root' in doc.embedded)

    def testDeleteLastEmbed(self):
        doc = self.doc("http://localhost/2")
        doc.embed('root', self.doc("http://localhost/"))
        doc.embed('child', self.doc("http://localhost/2/1"))

        target_doc = self.doc("http://localhost/2")

        doc.delete_embedded('root')
        doc.delete_embedded('child')

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteIndividualEmbeds(self):
        doc = self.doc("http://localhost/2")
        doc.embed('root', self.doc("http://localhost/"))
        doc.embed('child', self.doc("http://localhost/2/1"))
        doc.embed('child', self.doc("http://localhost/2/2"))
        doc.embed('child', self.doc("http://localhost/2/3"))

        doc2 = self.doc("http://localhost/2")
        doc2.embed('root', self.doc("http://localhost/"))
        doc2.embed('child', self.doc("http://localhost/2/2"))
        doc2.embed('child', self.doc("http://localhost/2/3"))

        doc3 = self.doc("http://localhost/2")
        doc3.embed('root', self.doc("http://localhost/"))
        doc3.embed('child', self.doc("http://localhost/2/2"))

        doc4 = self.doc("http://localhost/2")
        doc4.embed('root', self.doc("http://localhost/"))

        doc5 = self.doc("http://localhost/2")

        doc.delete_embedded("child", "http://localhost/2/1")
        self.assertEquals(doc2.as_object(), doc.as_object())

        doc.delete_embedded("child", "http://localhost/2/3")
        self.assertEquals(doc3.as_object(), doc.as_object())
        
        doc.delete_embedded("child", "http://localhost/2/2")
        self.assertEquals(doc4.as_object(), doc.as_object())

        doc.delete_embedded("root", "http://localhost/")
        self.assertEquals(doc5.as_object(), doc.as_object())

    def testDeleteEmbedsWithoutRel(self):
        doc = self.doc("http://localhost/3")
        doc.embed('child', self.doc("http://localhost/3/1"))
        doc.embed('child', self.doc("http://localhost/3/2"))
        doc.embed('favorite', self.doc("http://localhost/3/1"))

        target_doc = self.doc("http://localhost/3")
        target_doc.embed('child', self.doc("http://localhost/3/2"))

        doc.delete_embedded(href="http://localhost/3/1")

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteAllEmbeds(self):
        doc = self.doc("http://localhost/3")
        doc.embed('child', self.doc("http://localhost/3/1"))
        doc.embed('child', self.doc("http://localhost/3/2"))
        doc.embed('favorite', self.doc("http://localhost/3/1"))

        target_doc = self.doc("http://localhost/3")

        doc.delete_embedded()

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteEmbedWithMissingRel(self):
        doc = self.doc("http://localhost/3")
        doc.embed('child', self.doc("http://localhost/3/1"))
        doc.embed('child', self.doc("http://localhost/3/2"))
        doc.embed('favorite', self.doc("http://localhost/3/1"))

        target_doc = self.doc("http://localhost/3")
        target_doc.embed('child', self.doc("http://localhost/3/1"))
        target_doc.embed('child', self.doc("http://localhost/3/2"))
        target_doc.embed('favorite', self.doc("http://localhost/3/1"))

        missing_rel = ''.join(doc.embedded.keys()) + '_'
        doc.delete_embedded(missing_rel)

        self.assertEquals(target_doc.as_object(), doc.as_object())

    def testDeleteEmbedWithNoEmbeds(self):
        doc = self.doc("http://localhost/3")
        target_doc = self.doc("http://localhost/3")

        doc.delete_embedded()

        self.assertEquals(target_doc.as_object(), doc.as_object())


class CurieMutationTest(unittest.TestCase):
    def testSetCurie(self):
        doc = make_doc("http://localhost/3")
        doc.set_curie('rel', "http://localhost/rels/{relation}")

        new_doc = dougrain.Document(doc.as_object(), doc.relative_to_url)
        self.assertEquals("http://localhost/rels/foo",
                          new_doc.expand_curie("rel:foo"))

    def testReplaceCurie(self):
        doc = make_doc("http://localhost/3")
        doc.set_curie('rel', "http://localhost/rels/{relation}")
        doc.set_curie('rel', "http://localhost/RELS/{relation}.html")

        new_doc = dougrain.Document(doc.as_object(), doc.relative_to_url)
        self.assertEquals("http://localhost/RELS/foo.html",
                          new_doc.expand_curie("rel:foo"))

    def testDropCurie(self):
        doc = make_doc("http://localhost/3")
        doc.set_curie('rel', "http://localhost/rels/{relation}")
        doc.set_curie('tm', "http://www.touchmachine.com/{relation}.html")
        doc.drop_curie('rel')

        new_doc = dougrain.Document(doc.as_object(), doc.relative_to_url)
        self.assertEquals("rel:foo", doc.expand_curie("rel:foo"))
        self.assertEquals("http://www.touchmachine.com/index.html",
                          new_doc.expand_curie("tm:index"))


class CurieHidingTests(unittest.TestCase):
    def testCuriesAreNotLinks(self):
        doc = dougrain.Document({
            '_links': {
                'curie': {
                    'href': "http://localhost/rel/{relation}",
                    'name': "rel"
                },
                'self': {
                    'href': "http://localhost/0"
                }
            }
        }, "http://localhost/0")

        self.assertFalse('curie' in doc.links)
                

class EdgeCasesTests(unittest.TestCase):
    def testUrlOfDocumentWithMultipleSelfLinksFromFirstSelfLink(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.add_link('self', "/1")
        doc.add_link('self', "/2")
        self.assertEquals("http://localhost/1", doc.url())

    def testSetReservedAttributeSilentlyFails(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.set_attribute('_links', {'self': {'href': "/1"}})
        doc.set_attribute('_embedded', {'child': {'foo': "bar"}})

        self.assertFalse('_links' in doc.attrs)
        self.assertIsNone(doc.url())

        self.assertFalse('_embedded' in doc.attrs)
        self.assertFalse('child' in doc.embedded)

    def testDeleteReservedAttributeSilentlyFails(self):
        doc = dougrain.Document.empty("http://localhost")
        doc.embed('child', dougrain.Document.from_object({'foo': "bar"},
                                                         "http://localhost"))
        doc.add_link('self', "/1")

        with self.assertRaises(KeyError):
            doc.delete_attribute('_links')
        with self.assertRaises(KeyError):
            doc.delete_attribute('_embedded')

        self.assertFalse('_links' in doc.attrs)
        self.assertEquals("http://localhost/1", doc.url())

        self.assertFalse('_embedded' in doc.attrs)
        self.assertEquals("bar", doc.embedded['child'].attrs['foo'])


if __name__ == '__main__':
    unittest.main()
