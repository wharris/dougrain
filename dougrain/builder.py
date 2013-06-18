# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

from dougrain import drafts

class Builder(object):
    def __init__(self, uri, draft=drafts.LATEST):
        self.o = {'_links': {'self': {'href': uri}}}
        self.draft = draft.draft

    def set_property(self, name, value):
        self.o[name] = value

    def as_object(self):
        return self.o

    def add_link(self, rel, href, wrap=False, **kwargs):
        new_link = dict(href=href, **kwargs)

        if wrap:
            self.o['_links'].setdefault(rel, [])

        if not rel in self.o['_links']:
            self.o['_links'][rel] = new_link
            return

        existing_link = self.o['_links'][rel]
        if isinstance(existing_link, list):
            self.o['_links'][rel].append(new_link)
            return

        self.o['_links'][rel] = [existing_link, new_link]

    def add_curie(self, name, href):
        self.draft.set_curie(self, name, href)

