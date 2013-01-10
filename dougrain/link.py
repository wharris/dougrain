# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import urlparse
import re
import uritemplate

def extract_variables(href):
    patterns = [re.sub(r'\*|:\d+', '', pattern)
                for pattern in re.findall(r'{[\+#\./;\?&]?([^}]+)*}', href)]
    variables = []
    for pattern in patterns:
        for part in pattern.split(","):
            if not part in variables:
                variables.append(part)

    return variables


class Link(object):
    def __init__(self, json_object, relative_to_url):
        self.o = json_object
        self.href = json_object['href']

        if 'name' in json_object:
            self.name = json_object['name']

        if 'label' in json_object:
            self.label = json_object['label']

        self.variables = extract_variables(self.href)
        if relative_to_url is None:
            self.template = self.href
        else:
            self.template = urlparse.urljoin(relative_to_url, self.href)

    def url(self, **kwargs):
        return uritemplate.expand(self.template, kwargs)

    def as_object(self):
        return self.o

    @classmethod
    def from_object(cls, o, relative_to_url):
        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        return cls(o, relative_to_url)

    def __repr__(self):
        if hasattr(self, 'name'):
            return "<Link %s=%r>" % (self.name, self.template)
        else:
            return "<Link %r>" % self.template

    def __eq__(self, other):
        return (isinstance(other, Link) and
                self.as_object() == other.as_object())

