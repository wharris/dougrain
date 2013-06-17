# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

class Builder(object):
    def __init__(self, uri):
        self.o = {'_links': {'self': {'href': uri}}}

    def set_property(self, name, value):
        self.o[name] = value

    def as_object(self):
        return self.o

    def add_link(self, rel, href):
        self.o['_links'][rel] = {'href': href}

