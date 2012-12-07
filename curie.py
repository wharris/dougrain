#!/usr/bin/python
import urlparse

class CurieCollection(dict):
    def __init__(self, relative_to_url):
        self.relative_to_url = relative_to_url

    def expand(self, link):
        terms = link.split(':')

        if len(terms) < 2:
            return link

        key, value = terms

        if key not in self:
            return link

        return urlparse.urljoin(self.relative_to_url,
                                self[key].replace("{rel}", value))
