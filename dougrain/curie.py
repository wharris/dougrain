# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import urlparse
from random import choice


class CurieCollection(dict):
    def __init__(self, expansions_cache={}):
        # The default value of expansions_cache is not a mistake. The
        # dictionary is deliberately shared because the mapping between
        # (template, rel) and expansion is valid everywhere.
        super(CurieCollection, self).__init__()
        self.expansions_cache = expansions_cache

    EXPANSIONS_CACHE_LEN_LIMIT = 128

    def expand(self, link):
        terms = link.split(':')

        if len(terms) < 2:
            return link

        key, value = terms

        if key not in self:
            return link

        template = self[key]
        memo_key = template.href, value

        if memo_key in self.expansions_cache:
            return self.expansions_cache[memo_key]

        # Prevent unbounded growth of the shared cache.
        if len(self.expansions_cache) >= self.EXPANSIONS_CACHE_LEN_LIMIT:
            del self.expansions_cache[choice(self.expansions_cache.keys())]

        result = self[key].url(rel=value)
        self.expansions_cache[memo_key] = result

        return result
