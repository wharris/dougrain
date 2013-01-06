#!/usr/bin/python

import unittest
import dougrain

class ParseSimpleTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.from_object({"name": "David Bowman"})

    def testParseSimple(self):
        self.assertEquals(self.doc.name, "David Bowman")

    def testHasEmptyLinks(self):
        self.assertEquals(self.doc.links, {})

    def testHasAttrs(self):
        self.assertEquals(self.doc.attrs["name"], "David Bowman")


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
        self.assertEquals("Foo", foo.name)
        self.assertEquals(88888888, foo.size)

    def testLoadsArrayOfEmbeddedObjects(self):
        self.assertEquals(["Bar 1", "Bar 2"],
                          [bar.title for bar in self.doc.embedded['bar']])

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
        self.assertEquals("Client 1", consumer.name)

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

        self.assertEquals("bar", doc.foo)
        self.assertEquals("bar", doc.attrs['foo'])

    def testSetAttributeUpdatesAttribute(self):
        doc = dougrain.Document.empty()
        doc.set_attribute('foo', "bar")

        doc.set_attribute('foo', "bundy")

        self.assertEquals("bundy", doc.foo)
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


class LinkMutationTests(unittest.TestCase):
    def addLinks(self, from_doc, to_doc):
        for rel, links in from_doc.links.iteritems():
            if not isinstance(links, list):
                links = [links]
            for link in links:
                to_doc.add_link(rel, link)

    def testAddSimpleLink(self):
        target = {
            '_links': {
                'self': {'href': "http://localhost/1"}
            }
        }

        target_doc = dougrain.Document.from_object(target, "http://localhost/")

        doc = dougrain.Document.empty()
        self.addLinks(target_doc, doc)

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
        self.addLinks(target_doc, doc)

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
        self.addLinks(target_doc, doc)

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
        self.addLinks(target_doc, doc)

        self.assertEquals(target, doc.as_object())
        self.assertEquals(target_doc.links, doc.links)


if __name__ == '__main__':
    unittest.main()
