#!/usr/bin/python
import urlparse
import curie

class Document(object):
    def expand_curie(self, link):
        return self.curie.expand(link)

def from_json(o, relative_to_url=None, parent_curie=None):
    if isinstance(o, list):
        return map(lambda x: from_json(x, relative_to_url), o)

    def link_from_json(item):
        link = Document()
        link.__dict__.update(item)
        if relative_to_url is not None:
            link.url = urlparse.urljoin(relative_to_url, link.href)
        return link

    result = Document()
    result.attrs = o
    result.__dict__.update(o)
    result.links = {}

    for key, value in o.get("_links", {}).iteritems():
        if isinstance(value, list):
            result.links[key] = map(link_from_json, value)
        else:
            result.links[key] = link_from_json(value)

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
        result.embedded[key] = from_json(value,
                                         relative_to_url,
                                         result.curie)





    return result


