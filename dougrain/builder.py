# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

class Builder(object):
    def __init__(self, uri):
        self.o = {'_links': {'self': {'href': uri}}}

    def set_property(self, name, value):
        self.o[name] = value

    def as_object(self):
        return self.o

    def add_link(self, rel, href, **kwargs):
        new_link = dict(href=href, **kwargs)

        if not rel in self.o['_links']:
            self.o['_links'][rel] = new_link
            return

        existing_link = self.o['_links'][rel]
        if isinstance(existing_link, list):
            self.o['_links'][rel].append(new_link)
            return

        self.o['_links'][rel] = [existing_link, new_link]


