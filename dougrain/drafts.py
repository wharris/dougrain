# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""Draft-specific behaviours.

This module represents the differences between drafts of the HAL specification
and provides a mechanism for specifying the backwards-compatibility behavior of
Document instances.

Calling code is expected to use the following members:

    - ``DRAFT_3`` : the document should be compatible with Draft 3.
    - ``DRAFT_4`` : the document should be compatible with Draft 4.
    - ``DRAFT_5`` : the document should be compatible with Draft 5.
    - ``LATEST``  : the document should be compatible with the latest draft
                    implemented in this library.
    - ``AUTO``    : the document should be compatible with a draft level it
                    guesses from the JSON object with which it is initialized.

"""

LINKS_KEY = '_links'
EMBEDDED_KEY = '_embedded'


class Draft3(object):
    """Behaviour that is compatibile with draft 3 of the HAL spec.

    CURIEs are stored in a link with the relation type 'curie'. If there are
    multiple CURIEs, the document's JSON representation has a JSON array in
    ``_links.curie``, but if there is only one CURIE, ``_links.curie`` is a
    JSON object.

    See http://tools.ietf.org/html/draft-kelly-json-hal-03.
    """

    curies_rel = 'curie'
    automatic_link = False

    def set_curie(self, doc, name, href):
        doc.add_link(self.curies_rel, href, name=name, templated=True)


class Draft4(Draft3):
    """Behaviour that is compatibile with draft 4 of the HAL spec.

    CURIEs are stored in a link with the relation type 'curies'. If there
    are one or more CURIEs, the document's JSON representation has a JSON
    array in ``_links.curies``.

    See http://tools.ietf.org/html/draft-kelly-json-hal-04.
    """

    curies_rel = 'curies'

    def set_curie(self, doc, name, href):
        # CURIE links should always be in an array, even if there is only
        # one.
        doc.o.setdefault(LINKS_KEY, {}).setdefault(self.curies_rel, [])
        doc.o[LINKS_KEY][self.curies_rel].append(
            {'href': href, 'name': name, 'templated': True})


class Draft5(Draft4):
    """Behaviour that is compatibile with draft 5 of the HAL spec.

    CURIEs are stored in a link with the relation type 'curies'. If there
    are one or more CURIEs, the document's JSON representation has a JSON
    array in ``_links.curies``.

    If a document with a 'self' link is embedded and there is no
    corresponding link, a corresponding link is added.

    See http://tools.ietf.org/html/draft-kelly-json-hal-05.
    """

    automatic_link = True


class DraftIdentifier(object):
    """Identifies HAL draft level of a JSON document.

    When created with an existing JSON object, the document guesses the
    draft version based on the presence of a link with a relation type of
    'curie' or 'curies'.
    """

    def detect(self, obj):
        """Identifies the HAL draft level of a given JSON object."""
        links = obj.get(LINKS_KEY, {})

        for detector in [LATEST, DRAFT_3]:
            if detector.draft.curies_rel in links:
                return detector.detect(obj)

        return LATEST.detect(obj)

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class FixedDraftIdentifier(object):
    """Identifies JSON objects as having a known draft level."""

    def __init__(self, draft):
        self.draft = draft

    def detect(self, obj):
        """Identify the HAL draft level of obj as this instance's draft."""
        return self.draft

    def __eq__(self, other):
        if isinstance(other, FixedDraftIdentifier):
            return other.draft == self.draft

        return other == self.draft

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           self.draft.__class__.__name__)


DRAFT_3 = FixedDraftIdentifier(Draft3())
DRAFT_4 = FixedDraftIdentifier(Draft4())
DRAFT_5 = FixedDraftIdentifier(Draft5())
LATEST = DRAFT_5
AUTO = DraftIdentifier()
