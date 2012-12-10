#!/usr/bin/python
import urlparse

class Link(object):
    def __init__(self, json_object, relative_to_url):
        self.href = json_object['href']

        if relative_to_url is None:
            self.url = self.href
        else:
            self.url = urlparse.urljoin(relative_to_url, self.href)

        if 'name' in json_object:
            self.name = json_object['name']

        if 'label' in json_object:
            self.label = json_object['label']

    @classmethod
    def from_object(cls, o, relative_to_url):
        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        return cls(o, relative_to_url)


