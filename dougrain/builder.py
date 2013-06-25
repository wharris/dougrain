# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

from dougrain import drafts

class Builder(object):
    def __init__(self, href, draft=drafts.LATEST):
        self.o = {'_links': {'self': {'href': href}}}
        self.draft = draft.draft

    def url(self):
        return self.o['_links']['self']['href']

    def as_object(self):
        return self.o

    def add_curie(self, name, href):
        self.draft.set_curie(self, name, href)
        return self

    def set_property(self, name, value):
        self.o[name] = value
        return self

    def add_link(self, rel, target, wrap=False, **kwargs):
        if isinstance(target, str) or isinstance(target, unicode):
            new_link = dict(href=target, **kwargs)
        else:
            new_link = dict(href=target.url(), **kwargs)

        self.add_rel('_links', rel, new_link, wrap)
        return self

    def embed(self, rel, target, wrap=False):
        new_embed = target.as_object()
        self.add_rel('_embedded', rel, new_embed, wrap)

        if self.draft.automatic_link:
            self.add_link(rel, target, wrap)

        return self

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
