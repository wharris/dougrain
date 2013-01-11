# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""
Manipulating HAL documents.
"""

import urlparse
import itertools
import curie
import link
import UserDict
from functools import wraps

class Relationships(UserDict.DictMixin):
    """Merged view of relationships from a HAL document.

    Relationships, that is links and embedded documents, are presented as a
    dictionary-like object mapping the full URI of the relationship type to a
    list of relationships.
    
    If there are both embedded documents and links for the same relationship
    type, the embedded documents will be before the links. Otherwise,
    relationships are presented in the order they appear in their respective
    collection.

    Relationionships are deduplicated by their URL, as defined by their `self`
    link in the case of embedded documents and by their `href` in the case of
    links. Only the first relationship with that URL will be included.
    
    """
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
            self.prepare_cache()

    return deco


class Document(object):
    def __init__(self, o, relative_to_url, parent_curie=None):
        self.o = o
        self.parent_curie = parent_curie
        self.relative_to_url = relative_to_url
        self.prepare_cache()

    def prepare_cache(self):
        def attrs_cache():
            attrs = dict(self.o)
            attrs['_links'] = None
            del attrs['_links']
            attrs['_embedded'] = None
            del attrs['_embedded']
            return attrs

        def links_cache():
            links = {}

            for key, value in self.o.get("_links", {}).iteritems():
                if key == 'curie':
                    continue
                links[key] = link.Link.from_object(value, self.relative_to_url)

            return links

        def load_curie_collection():
            result = curie.CurieCollection()
            if self.parent_curie is not None:
                result.update(self.parent_curie)

            curies = link.Link.from_object(
                self.o.get('_links', {}).get('curie', []),
                self.relative_to_url)

            if not isinstance(curies, list):
                curies = [curies]

            for curie_link in curies:
                result[curie_link.name] = curie_link

            return result

        def embedded_cache():
            embedded = {}
            for key, value in self.o.get("_embedded", {}).iteritems():
                embedded[key] = self.from_object(value,
                                                 self.relative_to_url,
                                                 self.curie)
            return embedded

        self.attrs = attrs_cache()
        self.links = links_cache()
        self.curie = load_curie_collection()
        self.embedded = embedded_cache()
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

    def link(self, href, **kwargs):
        return link.Link(dict(href=href, **kwargs), self.relative_to_url)

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

    @mutator
    def delete_link(self, rel=None, href=lambda _: True):
        if rel is None:
            for rel in self.o['_links'].keys():
                self.delete_link(rel, href)
            return

        if callable(href):
            href_filter = href
        else:
            href_filter = lambda x: x == href

        links = self.o['_links']
        links_for_rel = links[rel]
        if isinstance(links_for_rel, dict):
            links_for_rel = [links_for_rel]

        new_links_for_rel = []
        for link in links_for_rel:
            if not href_filter(link['href']):
                new_links_for_rel.append(link)

        if new_links_for_rel:
            if len(new_links_for_rel) == 1:
                new_links_for_rel = new_links_for_rel[0]

            self.o['_links'][rel] = new_links_for_rel
        else:
            del self.o['_links'][rel]

        if not self.o['_links']:
            del self.o['_links']

    @classmethod
    def from_object(cls, o, relative_to_url=None, parent_curie=None):

        if isinstance(o, list):
            return map(lambda x: cls.from_object(x, relative_to_url), o)

        return cls(o, relative_to_url, parent_curie)

    @classmethod
    def empty(cls, relative_to_url=None):
        return cls.from_object({}, relative_to_url=relative_to_url)

    @mutator
    def embed(self, rel, other):
        embedded = self.o.setdefault('_embedded', {})
        links_for_rel = embedded.setdefault(rel, [])

        if isinstance(links_for_rel, dict):
            links_for_rel = [links_for_rel]

        links_for_rel.append(other.as_object())

        if len(links_for_rel) == 1:
            links_for_rel = links_for_rel[0]

        embedded[rel] = links_for_rel

    @mutator
    def delete_embedded(self, rel=None, self_href=lambda _: True):
        if rel is None:
            for rel in self.o['_embedded'].keys():
                self.delete_embedded(rel, self_href)
            return

        if callable(self_href):
            url_filter = self_href
        else:
            url_filter = lambda x: x == self_href

        rel_embeds = self.o['_embedded'][rel]

        if isinstance(rel_embeds, dict):
            del self.o['_embedded'][rel]

            if not self.o['_embedded']:
                del self.o['_embedded']
            return

        new_rel_embeds = []
        for embedded in list(rel_embeds):
            embedded_doc = Document(embedded, self.relative_to_url)
            if not url_filter(embedded_doc.url()):
                new_rel_embeds.append(embedded)

        if not new_rel_embeds:
            del self.o['_embedded'][rel]
        elif len(new_rel_embeds) == 1:
            self.o['_embedded'][rel] = new_rel_embeds[0]
        else:
            self.o['_embedded'][rel] = new_rel_embeds

        if not self.o['_embedded']:
            del self.o['_embedded']

    def set_curie(self, name, href):
        self.add_link('curie', self.link(href, name=name))

    @mutator
    def drop_curie(self, name):
        curies = self.o['_links']['curie']
        
        for i, curie in enumerate(curies):
            if curie['name'] == name:
                del curies[i]
                break

    def __eq__(self, other):
        if not isinstance(other, Document):
            return False
        
        return self.as_object() == other.as_object()

    def __repr__(self):
        return "<Document %r>" % self.url()



