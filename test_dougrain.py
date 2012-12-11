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
    def setUp(self):
        self.doc = dougrain.Document.from_object({
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
        }, relative_to_url="http://localhost/wharris/dougrain")

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

        self.assertEquals(self.doc.links["self"].url(), self.doc.url)

    def testLoadsLabel(self):
        self.assertEquals("Next", self.doc.links["next"].label)
        self.assertFalse(hasattr(self.doc.links["parent"], "label"))
        self.assertFalse(hasattr(self.doc.links["self"], "label"))

    def testLoadsArrayOfLinks(self):
        self.assertEquals(["/foo", "/bar"],
                          [link.href for link in self.doc.links['images']])


class ParseEmbeddedObjectsTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.from_object(
            {
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
            },
            relative_to_url="http://localhost/people/"
        )

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


class CurieExpansionTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.Document.from_object(
            {
                '_links': {
                    'curie': [
                        {
                            'href': "http://localhost/roles/{rel}",
                            'name': 'role',
                            'templated': True
                        },
                        {
                            'href': "http://localhost/images/",
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
                                    'href': "http://localhost/dimension/{rel}",
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
                                    'href': "http://localhost/imagefiles/{rel}",
                                    'name': 'image',
                                    'templated': True
                                }
                            ]
                        }
                    },
                }
            }
        )

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







if __name__ == '__main__':
    unittest.main()
