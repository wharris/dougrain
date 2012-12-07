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

