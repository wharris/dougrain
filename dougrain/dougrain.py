#!/usr/bin/python
import urlparse
import itertools
import curie
import link
import UserDict
from functools import wraps

class Relationships(UserDict.DictMixin):
    def __init__(self, links, embedded, curie):
        self.rels = {}

        item_urls = set()
        for key, values in itertools.chain(embedded.iteritems(),
                                           links.iteritems()):
            rel_key = curie.expand(key)
            if not isinstance(values, list):
                values = [values]

            for value in values:
                url = value.url()
                if url is not None and url in item_urls:
                    continue
                item_urls.add(url)
                
                self.rels.setdefault(rel_key, []).append(value)

    def __getitem__(self, key):
        return self.rels[key]

    def keys(self):
        return self.rels.keys()
         

def mutator(fn):
    @wraps(fn)
    def deco(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        finally:
            self.clear_cache()
            self.prepare_cache()

    return deco


class Document(object):
    def __init__(self, o, relative_to_url, parent_curie=None):
        self.o = o
        self.parent_curie = parent_curie
        self.relative_to_url = relative_to_url
        self.prepare_cache()

    TO_SAVE = "o parent_curie relative_to_url".split()

    def clear_cache(self):
        saves = dict((key, getattr(self, key))
                     for key in self.TO_SAVE)
        self.__dict__.clear()
        for key in self.TO_SAVE:
            setattr(self, key, saves[key])

    def attrs_cache(self):
        attrs = dict(self.o)
        attrs['_links'] = None
        del attrs['_links']
        attrs['_embedded'] = None
        del attrs['_embedded']
        return attrs

    def links_cache(self):
        links = {}

        for key, value in self.o.get("_links", {}).iteritems():
            links[key] = link.Link.from_object(value, self.relative_to_url)

        return links

    def load_curie_collection(self):
        result = curie.CurieCollection()
        if self.parent_curie is not None:
            result.update(self.parent_curie)

        curies = self.links.get('curie', [])
        if not isinstance(curies, list):
            curies = [curies]

        for curie_link in curies:
            result[curie_link.name] = curie_link

        return result

    def embedded_cache(self):
        embedded = {}
        for key, value in self.o.get("_embedded", {}).iteritems():
            embedded[key] = self.from_object(value,
                                             self.relative_to_url,
                                             self.curie)
        return embedded

    def prepare_cache(self):
        self.attrs = self.attrs_cache()
        self.__dict__.update(self.attrs)
        self.links = self.links_cache()
        self.curie = self.load_curie_collection()
        self.embedded = self.embedded_cache()
        self.rels = Relationships(self.links, self.embedded, self.curie)

    def url(self):
        if not 'self' in self.links:
            return None
        return self.links['self'].url()

    def expand_curie(self, link):
        return self.curie.expand(link)

    def as_object(self):
        return self.o

    @mutator
    def set_attribute(self, key, value):
        self.o[key] = value

    @mutator
    def delete_attribute(self, key):
        del self.o[key]

    @mutator
    def add_link(self, rel, link):
        links = self.o.setdefault('_links', {})
        new_link = link.as_object()
        if rel not in links:
            links[rel] = new_link
            return

        current_links = links[rel]
        if isinstance(current_links, list):
            current_links.append(new_link)
        else:
            links[rel] = [current_links, new_link]

    @classmethod
    def from_object(cls, o, relative_to_url=None, parent_curie=None):

        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        return cls(o, relative_to_url, parent_curie)

    @classmethod
    def empty(cls):
        return cls.from_object({})

    def __repr__(self):
        return "<Document %r>" % self.url()


