#!/usr/bin/python

import unittest
import dougrain

class ParseSimpleTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.from_json({"name": "David Bowman"})

    def testParseSimple(self):
        self.assertEquals(self.doc.name, "David Bowman")

    def testHasEmptyLinks(self):
        self.assertEquals(self.doc.links, {})

    def testHasAttrs(self):
        self.assertEquals(self.doc.attrs["name"], "David Bowman")

class ParseLinksTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.from_json({
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
                          self.doc.links["next"].url)

    def testLoadsRelativeURLHref(self):
        self.assertEquals("/wharris/",
                          self.doc.links["parent"].href)

    def testAbsolutesRelativeURL(self):
        self.assertEquals("http://localhost/wharris/",
                          self.doc.links["parent"].url)

    def testLoadsSelfAsLinkAndAttribute(self):
        self.assertEquals("dougrain", self.doc.links["self"].href)
        self.assertEquals("http://localhost/wharris/dougrain",
                          self.doc.links["self"].url)

        self.assertEquals(self.doc.links["self"].url, self.doc.url)

    def testLoadsLabel(self):
        self.assertEquals("Next", self.doc.links["next"].label)
        self.assertFalse(hasattr(self.doc.links["parent"], "label"))
        self.assertFalse(hasattr(self.doc.links["self"], "label"))

    def testLoadsArrayOfLinks(self):
        self.assertEquals(["/foo", "/bar"],
                          [link.href for link in self.doc.links['images']])


class ParseEmbeddedObjectsTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.from_json(
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
        self.assertEquals("http://localhost/people/2", link.url)


class CurieExpansionTest(unittest.TestCase):
    def setUp(self):
        self.doc = dougrain.from_json(
            {
                '_links': {
                    'curie': [
                        {
                            'href': 'http://localhost/roles/',
                            'name': 'role'
                        },
                        {
                            'href': 'http://localhost/images/',
                            'name': 'image'
                        }
                    ]
                }
            }
        )

    def testExposesCurieCollection(self):
        self.assertEquals("http://localhost/roles/category",
                          self.doc.expand_curie('role:category'))



if __name__ == '__main__':
    unittest.main()
