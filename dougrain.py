#!/usr/bin/python
import urlparse

class Document(object):
    pass

def from_json(o, relative_to_url=None):
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


    return result


