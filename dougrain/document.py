# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""
Manipulating HAL documents.
"""

import urlparse
import itertools
import curie
import link
import UserDict
from functools import wraps

class CanonicalRels(UserDict.DictMixin, object):
    """Smart querying of link relationship types and link relationships.

    A ``CanonicalRels`` instance is a read-only dictionary-like object that
    provides smart retrieval and de-duplication by link relationship type. It
    is used to make access to links and embedded resources more convenient.
    
    In addition to well-know link relationship types (eg. ``"self"``), keys can
    be custom link relationship types represented as URIs (eg.
    ``"http://example.com/rels/comments"``), or as URI references (eg.
    ``"/rels/comments"``), or as CURIEs (eg. ``"rel:comments"``).
    ``CanonicalRels`` treats custom link relationship types as equivalent if
    they expand to the same URI, called the canonical key here. Given a
    suitable base URI and set of CURIE templates,
    ``http://example.com/rels/comments``, ``/rels/comments``, and
    ``rel:comments`` are all equivalent.

    ``CanonicalRels`` de-duplicates items with equivalent keys.  De-duplication
    is achieved by appending the new values to the existing values for the
    canonical key. So, ``{"/rels/spam":eggs,"rel:spam":ham}`` becomes
    ``{"http://example.com/rels/spam":[eggs,ham]}``.

    Values can be retrieved using any key that is equivalent to the item's
    canonical key.

    """
    def __init__(self, rels, curies, base_uri, item_filter=lambda _: True):
        """Create a ``CanonicalRels`` instance.
        
        Arguments:

        - ``rels``:        the relationships to be queried. ``rels`` should be
                           a sequence of ``(key, value)`` tuples or an object
                           with an ``iteritems`` method that returns such a
                           sequence (such as a dictionary). For each tuple in
                           the sequence, ``key`` is a string that identifies
                           the link relationship type and ``value`` is the
                           target of the relationship or a sequence of targets
                           of the relationship.
        - ``curies``:      a ``CurieCollection`` used to expand CURIE keys.
        - ``base_uri``:    URL used as the basis when expanding keys that are
                           relative URI references.
        - ``item_filter``: optional filter on target relationships.
                           ``item_filter`` should be a callable that accepts a
                           target relationship and returns False if the target
                           relationship should be excluded. ``item_filter``
                           will be called once with each target relationship.

        """
        if hasattr(rels, 'iteritems'):
            items = rels.iteritems()
        else:
            items = rels

        self.curies = curies
        self.base_uri = base_uri
        self.rels = {}

        for key, value in items:
            canonical_key = self.canonical_key(key)
            if not canonical_key in self.rels:
                self.rels[canonical_key] = (key, value)
                continue

            original_key, current_value = self.rels[canonical_key]

            new_value = [item for item in current_value if item_filter(item)]
            new_value.extend(item for item in value if item_filter(item))
            self.rels[canonical_key] = original_key, new_value

        self.rels = self.rels

    def canonical_key(self, key):
        """Returns the canonical key for the given ``key``."""
        if key.startswith('/'):
            return urlparse.urljoin(self.base_uri, key)
        else:
            return self.curies.expand(key)

    def original_key(self, key):
        """Returns the first key seen for the given ``key``."""
        return self.rels[self.canonical_key(key)][0]

    def __getitem__(self, key):
        """Returns the link relationship that match the given ``key``.

        ``self[key]`` will return any link relationship who's key is equivalent
        to ``key``. Keys are equivalent if their canonical keys are equal.

        If there is more than one link relationship that matches ``key``, a
        list of matching link relationships is returned.

        If there is one link relationship that matches ``key``, that link
        relationship is returned.

        If there are no link relationships that match ``key``, a ``KeyError``
        is thrown.

        """
        return self.rels[self.canonical_key(key)][1]

    def __contains__(self, key):
        """Returns ``True`` if there are any link relationships for for
        ``self[key].``
        
        """
        return self.canonical_key(key) in self.rels

    def keys(self):
        """Returns a list of keys that map to every item.

        Each key returned is an original key. That is, the first key
        encountered for the canonical key.

        """
        return [original_key for original_key, _ in self.rels.itervalues()]


class Relationships(UserDict.DictMixin, object):
    """Merged view of relationships from a HAL document.

    Relationships, that is links and embedded resources, are presented as a
    dictionary-like object mapping the full URI of the link relationship type
    to a list of relationships.
    
    If there are both embedded resources and links for the same link relation
    type, the embedded resources will appear before the links. Otherwise,
    relationships are presented in the order they appear in their respective
    collection.

    Relationships are de-duplicated by their URL, as defined by their ``self``
    link in the case of embedded resources and by their ``href`` in the case of
    links. Only the first relationship with that URL will be included.
    
    """

    def __init__(self, links, embedded, curies, base_uri):
        """Initialize a ``Relationships`` object.

        Parameters:

        - ``links``:    a dictionary mapping a link relationship type to a
                        ``Link`` instance or a ``list`` of ``Link``
                        instances.
        - ``embedded``: a dictionary mapping a link relationship type to a
                        ``Document`` instance or a ``list`` of ``Document``
                        instances.
        - ``curies``:   a ``CurieCollection`` instance used to expand
                        link relationship type into full link relationship type
                        URLs.

        """
        rels = itertools.chain(embedded.iteritems(), links.iteritems())

        existing_urls = set()
        def item_filter(item):
            url = item.url()
            if url is not None and url in existing_urls:
                return False
            existing_urls.add(item.url())
            return True

        self.canonical_rels = CanonicalRels(rels, curies, base_uri, item_filter)

    def __getitem__(self, key):
        value = self.canonical_rels.__getitem__(key)
        if not isinstance(value, list):
            value = [value]
        return value

    def keys(self):
        return self.canonical_rels.keys()
         

def mutator(fn):
    """Decorator for ``Document`` methods that change the document.

    This decorator ensures that the object's caches are kept in sync
    when changes are made.
    
    """
    @wraps(fn)
    def deco(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        finally:
            self.prepare_cache()

    return deco


LINKS_KEY = '_links'
EMBEDDED_KEY = '_embedded'

class Draft(object):
    """Draft-specific behaviours."""

    class Draft3(object):
        """Behaviour that is compatibile with draft 3 of the HAL spec.

        See http://tools.ietf.org/html/draft-kelly-json-hal-03.
        """

        curies_rel = 'curie'

        def detect(self, obj):
            return self

        def set_curie(self, doc, name, href):
            doc.add_link(self.curies_rel, href, name=name, templated=True)

    class Draft4(object):
        """Behaviour that is compatibile with draft 4 of the HAL spec.

        See http://tools.ietf.org/html/draft-kelly-json-hal-04.
        """

        curies_rel = 'curies'

        def detect(self, obj):
            return self

        def set_curie(self, doc, name, href):
            # CURIE links should always be in an array, even if there is only
            # one.
            doc.o.setdefault(LINKS_KEY, {}).setdefault(self.curies_rel, [])
            doc.add_link(self.curies_rel, href, name=name, templated=True)

    class DraftAuto(object):
        """Behaviour for documents that automatically detect draft version."""
        def detect(self, obj):
            links = obj.get(LINKS_KEY, {})

            for draft in [Draft.DRAFT_4, Draft.DRAFT_3]:
                if draft.curies_rel in links:
                    return draft

            return Draft.DRAFT_4

    DRAFT_3 = Draft3()
    DRAFT_4 = Draft4()
    LATEST = DRAFT_4
    AUTO = DraftAuto()

class Document(object):
    """Represents the document for a HAL resource.

    Constructors:

    - ``Document.empty(base_uri=None)``:
        returns an empty ``Document``.
    - ``Document.from_object(o, base_uri=None, parent_curies=None)``:
        returns a new ``Document`` based on a JSON object.

    Public Instance Attributes:

    - ``properties``: ``dict`` containing the properties of the HAL document,
                      excluding ``_links`` and ``_embedded``. ``properties``
                      should be treated as read-only.
    - ``links``: ``dict`` containing the document's links, excluding
                 ``curies``. Each link relationship type is mapped to a ``Link``
                 instance or a list of ``Link`` instances. ``links`` should be
                 treated as read-only.
    - ``embedded``: dictionary containing the document's embedded resources.
                    Each link relationship type is mapped to a ``Document``
                    instance.
    - ``rels``: a ``Relationships`` instance holding a merged view of the
                relationships from the document.
    - ``draft``: a ``Draft`` instance that selects the version of the spec to
                 which the document should conform. Defaults to ``Draft.AUTO``.

    """
    def __init__(self, o, base_uri, parent_curies=None, draft=Draft.AUTO):
        self.o = o
        self.base_uri = base_uri
        self.parent_curies = parent_curies
        self.draft = draft.detect(o)
        self.prepare_cache()

    RESERVED_ATTRIBUTE_NAMES = (LINKS_KEY, EMBEDDED_KEY)

    def prepare_cache(self):
        def properties_cache():
            properties = dict(self.o)
            for name in self.RESERVED_ATTRIBUTE_NAMES:
                properties[name] = None
                del properties[name]
            return properties

        def links_cache():
            links = {}

            links_json = self.o.get(LINKS_KEY, {})

            for key, value in links_json.iteritems():
                if key == self.draft.curies_rel:
                    continue
                links[key] = link.Link.from_object(value, self.base_uri)

            return CanonicalRels(links, self.curies, self.base_uri)

        def load_curie_collection():
            result = curie.CurieCollection()
            if self.parent_curies is not None:
                result.update(self.parent_curies)

            links_json = self.o.get('_links', {})
            curies_json = links_json.get(self.draft.curies_rel)

            if not curies_json:
                return result

            curies = link.Link.from_object(curies_json, self.base_uri)

            if not isinstance(curies, list):
                curies = [curies]

            for curie_link in curies:
                result[curie_link.name] = curie_link

            return result

        def embedded_cache():
            embedded = {}
            for key, value in self.o.get(EMBEDDED_KEY, {}).iteritems():
                embedded[key] = self.from_object(value,
                                                 self.base_uri,
                                                 self.curies)
            return CanonicalRels(embedded, self.curies, self.base_uri)

        self.properties = properties_cache()
        self.curies = load_curie_collection()
        self.links = links_cache()
        self.embedded = embedded_cache()
        self.rels = Relationships(self.links, self.embedded, self.curies,
                                  self.base_uri)

    def url(self):
        """Returns the URL for the resource based on the ``self`` link.

        This method returns the ``href`` of the document's ``self`` link if it
        has one, or ``None`` if the document lacks a ``self`` link, or the
        ``href`` of the document's first ``self`` link if it has more than one.
        
        """
        if not 'self' in self.links:
            return None

        self_link = self.links['self']

        if isinstance(self_link, list):
            for link in self_link:
                return link.url()

        return self_link.url()

    def expand_curie(self, link):
        """Returns the expansion of a CURIE value.

        Arguments:
        - ``link``: a string holding a curie value to expand.

        This method attempts to expand ``link`` using the document's ``curies``
        collection (see ``curie.CurieCollection.expand``).

        """
        return self.curies.expand(link)

    def as_object(self):
        """Returns a dictionary representing the HAL JSON document."""
        return self.o

    def as_link(self):
        """Returns a ``Link`` to the resource."""
        return self.links['self']

    @mutator
    def set_property(self, key, value):
        """Set a property on the document.

        Calling code should use this method to add and modify properties
        on the document instead of modifying ``properties`` directly.

        If ``key`` is ``"_links"`` or ``"_embedded"`` this method will silently
        fail.

        If there is no property with the name in ``key``, a new property is
        created with the name from ``key`` and the value from ``value``. If
        the document already has a property with that name, it's value
        is replaced with the value in ``value``.

        """
        if key in self.RESERVED_ATTRIBUTE_NAMES:
            return
        self.o[key] = value

    @mutator
    def delete_property(self, key):
        """Remove an property from the document.

        Calling code should use this method to remove properties on the
        document instead of modifying ``properties`` directly.

        If there is a property with the name in ``key``, it will be removed.
        Otherwise, a ``KeyError`` will be thrown.

        """
        if key in self.RESERVED_ATTRIBUTE_NAMES:
            raise KeyError(key)
        del self.o[key]

    def link(self, href, **kwargs):
        """Retuns a new link relative to this resource."""
        return link.Link(dict(href=href, **kwargs), self.base_uri)

    @mutator
    def add_link(self, rel, target, **kwargs):
        """Adds a link to the document.

        Calling code should use this method to add links instead of
        modifying ``links`` directly.
        
        This method adds a link to the given ``target`` to the document with
        the given ``rel``. If one or more links are already present for that
        link relationship type, the new link will be added to the existing
        links for that link relationship type.

        If ``target`` is a string, a link is added with ``target`` as its
        ``href`` property and other properties from the keyword arguments.

        If ``target`` is a ``Link`` object, it is added to the document and the
        keyword arguments are ignored.

        If ``target`` is a ``Document`` object, ``target``'s ``self`` link is
        added to this document and the keyword arguments are ignored.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the link.
          It should be a well-known link relation name from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``target``: the destination of the link.

        """
        if hasattr(target, 'as_link'):
            link = target.as_link()
        else:
            link = self.link(target, **kwargs)

        links = self.o.setdefault(LINKS_KEY, {})
        
        new_link = link.as_object()
        collected_links = CanonicalRels(links, self.curies, self.base_uri)
        if rel not in collected_links:
            links[rel] = new_link
            return

        original_rel = collected_links.original_key(rel)

        current_links = links[original_rel]
        if isinstance(current_links, list):
            current_links.append(new_link)
        else:
            links[original_rel] = [current_links, new_link]

    @mutator
    def delete_link(self, rel=None, href=lambda _: True):
        """Deletes links from the document.

        Calling code should use this method to remove links instead of
        modyfying ``links`` directly.

        The optional arguments, ``rel`` and ``href`` are used to select the
        links that will be deleted. If neither of the optional arguments are
        given, this method deletes every link in the document. If ``rel`` is
        given, only links for the matching link relationship type are deleted.
        If ``href`` is given, only links with a matching ``href`` are deleted.
        If both ``rel`` and ``href`` are given, only links with matching
        ``href`` for the matching link relationship type are delted.

        Arguments:

        - ``rel``: an optional string specifying the link relationship type of
                   the links to be deleted.
        - ``href``: optionally, a string specifying the ``href`` of the links
                    to be deleted, or a callable that returns true when its
                    single argument is in the set of ``href``s to be deleted.

        """
        if not LINKS_KEY in self.o:
            return

        links = self.o[LINKS_KEY]
        if rel is None:
            for rel in links.keys():
                self.delete_link(rel, href)
            return

        if callable(href):
            href_filter = href
        else:
            href_filter = lambda x: x == href

        links_for_rel = links.setdefault(rel, [])
        if isinstance(links_for_rel, dict):
            links_for_rel = [links_for_rel]

        new_links_for_rel = []
        for link in links_for_rel:
            if not href_filter(link['href']):
                new_links_for_rel.append(link)

        if new_links_for_rel:
            if len(new_links_for_rel) == 1:
                new_links_for_rel = new_links_for_rel[0]

            links[rel] = new_links_for_rel
        else:
            del links[rel]

        if not self.o[LINKS_KEY]:
            del self.o[LINKS_KEY]

    @classmethod
    def from_object(cls, o, base_uri=None, parent_curies=None,
                    draft=Draft.AUTO):
        """Returns a new ``Document`` based on a JSON object or array.

        Arguments:

        - ``o``: a dictionary holding the deserializated JSON for the new
                 ``Document``, or a ``list`` of such documents.
        - ``base_uri``: optional URL used as the basis when expanding
                               relative URLs in the document.
        - ``parent_curies``: optional ``CurieCollection`` instance holding the
                             CURIEs of the parent document in which the new
                             document is to be embedded. Calling code should not
                             normally provide this argument.
        - ``draft``: a ``Draft`` instance that selects the version of the spec
                     to which the document should conform. Defaults to
                     ``Draft.AUTO``.

        """

        if isinstance(o, list):
            return map(lambda x: cls.from_object(x,
                                                 base_uri,
                                                 parent_curies,
                                                 draft),
                       o)

        return cls(o, base_uri, parent_curies, draft)

    @classmethod
    def empty(cls, base_uri=None, draft=Draft.AUTO):
        """Returns an empty ``Document``.

        Arguments:

        - ``base_uri``: optional URL used as the basis when expanding
                               relative URLs in the document.
        - ``draft``: a ``Draft`` instance that selects the version of the spec
                     to which the document should conform. Defaults to
        """
        return cls.from_object({}, base_uri=base_uri, draft=draft)

    @mutator
    def embed(self, rel, other):
        """Embeds a document inside this document.

        Arguments:

        - ``rel``: a string specifying the link relationship type of the
          embedded resource. ``rel`` should be a well-known link relation name
          from the IANA registry
          (http://www.iana.org/assignments/link-relations/link-relations.xml),
          a full URI, or a CURIE.
        - ``other``: a ``Document`` instance that will be embedded in this
          document.

        Calling code should use this method to add embedded resources instead
        of modifying ``embedded`` directly.
        
        This method embeds the given document in this document with the given
        ``rel``. If one or more documents have already been embedded for that
        ``rel``, the new document will be embedded in addition to those
        documents.

        """
        embedded = self.o.setdefault(EMBEDDED_KEY, {})
        collected_embedded = CanonicalRels(embedded, self.curies, self.base_uri)

        if rel not in collected_embedded:
            embedded[rel] = other.as_object()
            return

        original_rel = collected_embedded.original_key(rel)

        current_embedded = embedded[original_rel]
        if isinstance(current_embedded, list):
            current_embedded.append(other.as_object())
        else:
            embedded[original_rel] = [current_embedded, other.as_object()]

    @mutator
    def delete_embedded(self, rel=None, href=lambda _: True):
        """Removes an embedded resource from this document.

        Calling code should use this method to remove embedded resources
        instead of modifying ``embedded`` directly.

        The optional arguments, ``rel`` and ``href`` are used to select the
        embedded resources that will be removed. If neither of the optional
        arguments are given, this method removes every embedded resource from
        this document. If ``rel`` is given, only embedded resources for the
        matching link relationship type are removed. If ``href`` is given, only
        embedded resources with a ``self`` link matching ``href`` are deleted.
        If both ``rel`` and ``href`` are given, only embedded resources with
        matching ``self`` link for the matching link relationship type are
        removed.

        Arguments:

        - ``rel``: an optional string specifying the link relationship type of
                   the embedded resources to be removed.
        - ``href``: optionally, a string specifying the ``href`` of the
                    ``self`` links of the resources to be removed, or a
                    callable that returns true when its single argument matches
                    the ``href`` of the ``self`` link of one of the resources
                    to be removed.

        """
        if EMBEDDED_KEY not in self.o:
            return

        if rel is None:
            for rel in self.o[EMBEDDED_KEY].keys():
                self.delete_embedded(rel, href)
            return

        if rel not in self.o[EMBEDDED_KEY]:
            return

        if callable(href):
            url_filter = href
        else:
            url_filter = lambda x: x == href

        rel_embeds = self.o[EMBEDDED_KEY][rel]

        if isinstance(rel_embeds, dict):
            del self.o[EMBEDDED_KEY][rel]

            if not self.o[EMBEDDED_KEY]:
                del self.o[EMBEDDED_KEY]
            return

        new_rel_embeds = []
        for embedded in list(rel_embeds):
            embedded_doc = Document(embedded, self.base_uri)
            if not url_filter(embedded_doc.url()):
                new_rel_embeds.append(embedded)

        if not new_rel_embeds:
            del self.o[EMBEDDED_KEY][rel]
        elif len(new_rel_embeds) == 1:
            self.o[EMBEDDED_KEY][rel] = new_rel_embeds[0]
        else:
            self.o[EMBEDDED_KEY][rel] = new_rel_embeds

        if not self.o[EMBEDDED_KEY]:
            del self.o[EMBEDDED_KEY]

    def set_curie(self, name, href):
        """Sets a CURIE.

        A CURIE link with the given ``name`` and ``href`` is added to the
        document.

        """

        self.draft.set_curie(self, name, href)

    @mutator
    def drop_curie(self, name):
        """Removes a CURIE.

        The CURIE link with the given name is removed from the document.

        """
        curies = self.o[LINKS_KEY][self.draft.curies_rel]
        if isinstance(curies, dict) and curies['name'] == name:
            del self.o[LINKS_KEY][self.draft.curies_rel]
            return
        
        for i, curie in enumerate(curies):
            if curie['name'] == name:
                del curies[i]
                break
                
            continue

    def __iter__(self):
        yield self

    def __eq__(self, other):
        if not isinstance(other, Document):
            return False
        
        return self.as_object() == other.as_object()

    def __repr__(self):
        return "<Document %r>" % self.url()



