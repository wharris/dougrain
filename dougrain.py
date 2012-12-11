#!/usr/bin/python
import urlparse
import curie
import link

class Document(object):
    def __init__(self, o, relative_to_url, parent_curie=None):
        self.attrs = o
        self.__dict__.update(o)
        self.links = {}

        for key, value in o.get("_links", {}).iteritems():
            self.links[key] = link.Link.from_object(value, relative_to_url)

        if 'self' in self.links:
            self.url = self.links['self'].url()

        self.curie = curie.CurieCollection()
        if parent_curie is not None:
            self.curie.update(parent_curie)

        curies = self.links.get('curie', [])
        if not isinstance(curies, list):
            curies = [curies]

        for curie_link in curies:
            self.curie[curie_link.name] = curie_link

        self.embedded = {}
        for key, value in o.get("_embedded", {}).iteritems():
            self.embedded[key] = self.__class__.from_object(value,
                                                            relative_to_url,
                                                            self.curie)

    def expand_curie(self, link):
        return self.curie.expand(link)

    @classmethod
    def from_object(cls, o, relative_to_url=None, parent_curie=None):

        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        return cls(o, relative_to_url, parent_curie)



