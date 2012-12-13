#!/usr/bin/python
import unittest
import link

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

    def testLabelIsMissing(self):
        self.assertFalse(hasattr(self.link, 'label'))


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

    def testLabelIsMissing(self):
        self.assertFalse(hasattr(self.link, 'label'))


class TestParseAdditionalAttributes(unittest.TestCase):
    def setUp(self):
        self.link = link.Link(
            {
                'href': "/foo",
                'name': "bar",
                'label': "Bar"
            },
            "http://localhost/"
        )

    def testLoadsName(self):
        self.assertEquals("bar", self.link.name)

    def testLoadsLabel(self):
        self.assertEquals("Bar", self.link.label)


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


if __name__ == '__main__':
    unittest.main()
