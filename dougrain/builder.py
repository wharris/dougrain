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

    def add_rel(self, key, rel, thing, wrap):
        self.o.setdefault(key, {})

        if wrap:
            self.o[key].setdefault(rel, [])

        if rel not in self.o[key]:
            self.o[key][rel] = thing
            return

        existing = self.o[key].get(rel)
        if isinstance(existing, list):
            existing.append(thing)
            return

        self.o[key][rel] = [existing, thing]

    def add_link(self, rel, href, wrap=False, **kwargs):
        new_link = dict(href=href, **kwargs)
        self.add_rel('_links', rel, new_link, wrap)

    def embed(self, rel, target, wrap=False):
        new_embed = target.as_object()
        self.add_rel('_embedded', rel, new_embed, wrap)

    def add_curie(self, name, href):
        self.draft.set_curie(self, name, href)

