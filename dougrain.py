#!/usr/bin/python
import urlparse
import curie
import link

class Document(object):
    def expand_curie(self, link):
        return self.curie.expand(link)

    @classmethod
    def from_object(cls, o, relative_to_url=None, parent_curie=None):

        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        result = Document()
        result.attrs = o
        result.__dict__.update(o)
        result.links = {}

        for key, value in o.get("_links", {}).iteritems():
            result.links[key] = link.Link.from_object(value, relative_to_url)

        if 'self' in result.links:
            result.url = result.links['self'].url

        result.curie = curie.CurieCollection(relative_to_url)
        if parent_curie is not None:
            result.curie.update(parent_curie)

        curies = result.links.get('curie', [])
        if not isinstance(curies, list):
            curies = [curies]
        for curie_dict in curies:
            result.curie[curie_dict.name] = curie_dict.href

        result.embedded = {}
        for key, value in o.get("_embedded", {}).iteritems():
            result.embedded[key] = cls.from_object(value,
                                                   relative_to_url,
                                                   result.curie)

        return result

