# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""
Creating HAL documents.
"""

from dougrain import drafts
from dougrain import link

try:
    _ = unicode
except NameError:
    unicode = str


class Builder(object):
    """Simplify creation of HAL documents.

    ``Builder`` provides a lightweight chainable API for creating HAL
    documents.

    Unlike ``dougrain.Document``, ``Builder`` provides no facilities for
    interrogating or mutating existing documents. ``Builder`` also makes fewer
    sanity checks than ``dougrain.Document``, which makes it considerably
    faster, but more likely to produce invalid HAL documents.

    """

    def __init__(self, href, draft=drafts.LATEST, **kwargs):
        """``Builder(href, draft=drafts.LATEST, **kwargs)``

        Make a builder for a document. The document starts with a ``self``
        link to ``href``.

        The version of the spec may be specified in the optional ``draft``
        argument, which defaults to the latest draft. For example, to build a
        document conforming to the older Draft 4 of the spec:

        ``
        dougrain.Document("/test", draft=dougrain.drafts.DRAFT_4)
        ``

        Additional properties for the self link may be supplied in other
        keyword arguments. For example:

        ``
        dougrain.Document("/test", profile="/profiles/")
        ``

        """
        self.o = {'_links': {'self': dict(href=href, **kwargs)}}
        self.draft = draft.draft

    def url(self):
        """Returns the URL for the resource based on the ``self`` link.

        This method is used when embedding a ``Builder`` in a
        ``dougrain.Document``.
        """
        return self.o['_links']['self']['href']

    def as_object(self):
        """Returns a dictionary representing the HAL JSON document."""
        return self.o

    def as_link(self):
        """Returns a ``Link`` to the document.

        This method is used when adding a link to a ``Builder`` from a
        ``dougrain.Document``.
        """
        return link.Link(self.o['_links']['self'], None)

    def add_curie(self, name, href):
        """Adds a CURIE definition.

        A CURIE link with the given ``name`` and ``href`` is added to the
        document.

        This method returns self, allowing it to be chained with additional
        method calls.
        """
        self.draft.set_curie(self, name, href)
        return self

    def set_property(self, name, value):
        """Set a property on the document.

        If there is no property with the name in ``name``, a new property is
        created with the name from ``name`` and the value from ``value``. If
        the document already has a property with that name, it's value
        is replaced with the value in ``value``.

        This method returns self, allowing it to be chained with additional
        method calls.

        WARNING: ``name`` should not be one of the reserved property
        names (``'_links'`` or ``'_embedded'``). If ``name`` is ``'_links'`` or
        ``'_embedded'``, this method may silently corrupt the JSON object
        representation and cause undefined behaviour later.

        """
        self.o[name] = value
        return self

    def add_link(self, rel, target, wrap=False, **kwargs):
        """Adds a link to the document.

        This method adds a link to the given ``target`` to the document with
        the given ``rel``. If one or more links are already present for that
        link relationship type, the new link will be added to the existing
        links for that link relationship type.

        Unlike ``dougrain.Document.add_link``, this method does not detect
        equivalence between relationship types with different representations.

        If ``target`` is a string, a link is added with ``target`` as its
        ``href`` property and other properties from the keyword arguments.

        If ``target`` is a ``dougrain.Document`` object, a link is added with
        ``target``'s URL as its ``href`` property and other property from the
        keyword arguments.

        If ``target`` is a ``Builder`` object, a link is added with
        ``target``'s URL as its ``href`` property and other property from the
        keyword arguments.

        This method returns self, allowing it to be chained with additional
        method calls.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the link.
          It should be a well-known link relation name from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``target``: the destination of the link.
        - ``wrap``: Defaults to False, but if True, specifies that the link
          object should be initally wrapped in a JSON array even if it is the
          first link for the given ``rel``.

        """
        if isinstance(target, bytes):
            target = target.decode('utf-8')
        if isinstance(target, str) or isinstance(target, unicode):
            new_link = dict(href=target, **kwargs)
        else:
            new_link = dict(href=target.url(), **kwargs)

        self._add_rel('_links', rel, new_link, wrap)
        return self

    def embed(self, rel, target, wrap=False):
        """Embeds a document inside this document.

        This method embeds the given document in this document with the given
        ``rel``. If one or more documents have already been embedded for that
        ``rel``, the new document will be embedded in addition to those
        documents.

        This method returns self, allowing it to be chained with additional
        method calls.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the
          embedded resource. ``rel`` should be a well-known link relation name
          from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``target``: a ``Builder`` instance or a ``dougrain.Document``
          instance that will be embedded in this document.
        - ``wrap``: Defaults to False, but if True, specifies that the embedded
          resource object should be initally wrapped in a JSON array even if it
          is the first embedded resource for the given ``rel``.

        Unlike ``dougrain.Document.embed``, this method does not detect
        equivalence between relationship types with different representations.

        WARNING: ``target`` should not be identical to ``self`` or any document
        that embeds ``self``.
        """
        new_embed = target.as_object()
        self._add_rel('_embedded', rel, new_embed, wrap)

        if self.draft.automatic_link:
            self.add_link(rel, target, wrap)

        return self

    def _add_rel(self, key, rel, thing, wrap):
        """Adds ``thing`` to links or embedded resources.

        Calling code should not use this method directly and should use
        ``embed`` or ``add_link`` instead.

        """
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
