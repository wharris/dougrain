# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.
"""Draft-specific behaviours."""

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

    def detect(self, obj):
        return self

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
        doc.add_link(self.curies_rel, href, name=name, templated=True)


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


class DraftAuto(object):
    """Behaviour for documents that automatically detect draft version.
    
    When created with an existing JSON object, the document guesses the
    draft version based on the presence of a link with a relation type of
    'curie' or 'curies'.
    """

    def detect(self, obj):
        links = obj.get(LINKS_KEY, {})

        for draft in [LATEST, DRAFT_3]:
            if draft.curies_rel in links:
                return draft

        return LATEST


DRAFT_3 = Draft3()
DRAFT_4 = Draft4()
DRAFT_5 = Draft5()
LATEST = DRAFT_5
AUTO = DraftAuto()



