#!/usr/bin/python
# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import unittest
from dougrain import link

class TestParseAbsoluteLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {'href': "http://localhost/"},
            None)

    def testLoadsAbsoluteHref(self):
        self.assertEquals("http://localhost/", self.link.href)

    def testCalculatesUrl(self):
        self.assertEquals("http://localhost/", self.link.url())

    def testNameIsMissing(self):
        self.assertFalse(hasattr(self.link, 'name'))

    def testTitleIsMissing(self):
        self.assertFalse(hasattr(self.link, 'title'))


class TestParseRelativeLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {'href': "/foo"},
            "http://localhost/")

    def testLoadsAbsoluteHref(self):
        self.assertEquals("/foo", self.link.href)

    def testCalculatesUrl(self):
        self.assertEquals("http://localhost/foo", self.link.url())

    def testNameIsMissing(self):
        self.assertFalse(hasattr(self.link, 'name'))

    def testTitleIsMissing(self):
        self.assertFalse(hasattr(self.link, 'title'))


class TestParseAdditionalAttributes(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo",
                'name': "bar",
                'title': "Bar",
                'type': "application/hal+json",
                'profile': "/profiles/foo",
                'hreflang': "en"
            },
            "http://localhost/"
        )

    def testLoadsName(self):
        self.assertEquals("bar", self.link.name)

    def testLoadsTitle(self):
        self.assertEquals("Bar", self.link.title)

    def testLoadsType(self):
        self.assertEquals("application/hal+json", self.link.type)

    def testLoadsProfile(self):
        self.assertEquals("/profiles/foo", self.link.profile)

    def testLoadsHreflang(self):
        self.assertEquals("en", self.link.hreflang)


class TestExpandTemplatedLink(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo/{arg1}",
                'templated': True
            },
            "http://localhost/"
        )

    def testHasArgs(self):
        self.assertEquals(["arg1"], self.link.variables)

    def testSubstituteNoArgs(self):
        self.assertEquals("http://localhost/foo/", self.link.url())

    def testSubstituteArg(self):
        self.assertEquals("http://localhost/foo/1-bar",
                          self.link.url(arg1="1-bar"))

    def testPreservesTemplate(self):
        self.assertEquals("http://localhost/foo/{arg1}", self.link.template)


class TestDoNotExpandNonTemplateLinks(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo/{arg1}"
            },
            "http://localhost/"
        )

    def testHasNoArgs(self):
        self.assertEquals([], self.link.variables)

    def testSubstituteNoArgs(self):
        self.assertEquals("http://localhost/foo/{arg1}", self.link.url())

    def testSubstituteArg(self):
        self.assertEquals("http://localhost/foo/{arg1}",
                          self.link.url(arg1="1-bar"))

    def testPreservesTemplate(self):
        self.assertEquals("http://localhost/foo/{arg1}", self.link.template)


class TestExtractVariablesFromLink(unittest.TestCase):
    def assertVariables(self, variables, href):
        if isinstance(variables, str):
            variables = variables.split()

        lnk = link.Link(
            {
                'href': href,
                'templated': True
            },
            "http://localhost/"
        )
        self.assertEquals(variables, lnk.variables)

    def testNoVariables(self):
        self.assertVariables([], "/index.html")

    def testSingleVariableLevel1(self):
        self.assertVariables('var', "{var}")
        self.assertVariables('hello', "{hello}")

    def testUrlEncodeVariableLevel2(self):
        self.assertVariables("var", "{+var}")
        self.assertVariables("hello", "{+hello}")
        self.assertVariables("path", "{+path}/here")
        self.assertVariables("path", "here?ref={+path}")

    def testMultipleVariablesLevel3(self):
        self.assertVariables("x y", "map?{x,y}")
        self.assertVariables("x hello y", "{x,hello,y}")
        self.assertVariables("x hello y", "{+x,hello,y}")
        self.assertVariables("path x", "{+path,x}/here")
        self.assertVariables("x hello y", "{#x,hello,y}")
        self.assertVariables("path x", "{#path,x}/here")
        self.assertVariables("var", "X{.var}")
        self.assertVariables("x y", "X{.x,y}")
        self.assertVariables("var", "{/var}")
        self.assertVariables("var x", "{/var,x}/here")
        self.assertVariables("x y", "{;x,y}")
        self.assertVariables("x y empty", "{;x,y,empty}")
        self.assertVariables("x y", "{?x,y}")
        self.assertVariables("x y empty", "{?x,y,empty}")
        self.assertVariables("x", "?fixed=yes{&x}")
        self.assertVariables("x y empty", "{&x,y,empty}")

    def testLevel4(self):
      self.assertVariables("var", "{var:3}")
      self.assertVariables("var", "{var:30}")
      self.assertVariables("list", "{list}")
      self.assertVariables("list", "{list*}")
      self.assertVariables("keys", "{keys}")
      self.assertVariables("keys", "{keys*}")
      self.assertVariables("path", "{+path:6}/here")
      self.assertVariables("list", "{+list}")
      self.assertVariables("list", "{+list*}")
      self.assertVariables("keys", "{+keys}")
      self.assertVariables("keys", "{+keys*}")
      self.assertVariables("path", "{#path:6}/here")
      self.assertVariables("list", "{#list}")
      self.assertVariables("list", "{#list*}")
      self.assertVariables("keys", "{#keys}")
      self.assertVariables("keys", "{#keys*}")
      self.assertVariables("var", "X{.var:3}")
      self.assertVariables("list", "X{.list}")
      self.assertVariables("list", "X{.list*}")
      self.assertVariables("keys", "X{.keys}")
      self.assertVariables("var", "{/var:1,var}")
      self.assertVariables("list", "{/list}")
      self.assertVariables("list", "{/list*}")
      self.assertVariables("list path", "{/list*,path:4}")
      self.assertVariables("keys", "{/keys}")
      self.assertVariables("keys", "{/keys*}")
      self.assertVariables("hello", "{;hello:5}")
      self.assertVariables("list", "{;list}")
      self.assertVariables("list", "{;list*}")
      self.assertVariables("keys", "{;keys}")
      self.assertVariables("keys", "{;keys*}")
      self.assertVariables("var", "{?var:3}")
      self.assertVariables("list", "{?list}")
      self.assertVariables("list", "{?list*}")
      self.assertVariables("keys", "{?keys}")
      self.assertVariables("keys", "{?keys*}")
      self.assertVariables("var", "{&var:3}")
      self.assertVariables("list", "{&list}")
      self.assertVariables("list", "{&list*}")
      self.assertVariables("keys", "{&keys}")
      self.assertVariables("keys", "{&keys*}")


class TestIteration(unittest.TestCase):
    def testASingleLinkCanBeIterated(self):
        the_link = link.Link({"href": "/"}, "http://localhost/")
        count = 0
        for a_link in the_link:
            count += 1
            self.assertEquals(the_link, a_link)

        self.assertEquals(1, count)


if __name__ == '__main__':
    unittest.main()
