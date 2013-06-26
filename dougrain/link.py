# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import urlparse
import re
import uritemplate


def extract_variables(href):
    """Return a list of variable names used in a URI template."""

    patterns = [re.sub(r'\*|:\d+', '', pattern)
                for pattern in re.findall(r'{[\+#\./;\?&]?([^}]+)*}', href)]
    variables = []
    for pattern in patterns:
        for part in pattern.split(","):
            if not part in variables:
                variables.append(part)

    return variables


class Link(object):
    """Representation of a HAL link from a ``Document``.

    Constructors:

    - ``Link.from_object(o, base_uri=None)``:
        returns a new ``Link`` based on a JSON object.

    Public Instance Attributes:

    - ``href``: ``str`` containing the href of the link.
    - ``name``: ``str`` containing the name of the link. Absent if the link
                has no name.
    - ``title``: ``str`` containing the title of the link. Absent if the link
                 has no title.
    - ``type``: ``str`` containing the type of the link. Absent if the link
                does not specify a type.
    - ``profile``: ``str`` containing the profile URL reference of the link.
                   Absent if the link does not specify a profile.
    - ``hreflang``: ``str`` indicating the language of the target. Absent if
                    the link does not specify a language.
    - ``deprecation``: ``str`` indicating that the link is deprecated. The
                       value of the string should be a URL that provides
                       further infomation about the deprecation. Absent if the
                       link is not marked as deprecated.
    - ``variables``: ``list`` of names of template variables that may be
                     expanded for templated links. Empty if there are no
                     template variables.

    """
    def __init__(self, json_object, base_uri):
        self.o = json_object
        self.href = json_object['href']

        if 'name' in json_object:
            self.name = json_object['name']

        if 'title' in json_object:
            self.title = json_object['title']

        if 'type' in json_object:
            self.type = json_object['type']

        if 'profile' in json_object:
            self.profile = json_object['profile']

        if 'hreflang' in json_object:
            self.hreflang = json_object['hreflang']

        if 'deprecation' in json_object:
            self.deprecation = json_object['deprecation']

        self.is_templated = self.o.get('templated', False) is True

        if self.is_templated:
            self.variables = extract_variables(self.href)
        else:
            self.variables = []

        if base_uri is None:
            self.template = self.href
        else:
            self.template = urlparse.urljoin(base_uri, self.href)

    def url(self, **kwargs):
        """Returns a URL for the link with optional template expansion.

        If the link is marked as templated, the href will be expanded according
        to RFC6570, using template variables provided in the keyword arguments.
        If the href is a valid URI Template, but the link is not marked as
        templated, the href will not be expanded even if template variables are
        provided.

        """
        if self.is_templated:
            return uritemplate.expand(self.template, kwargs)
        else:
            return self.template

    def as_object(self):
        """Returns a dictionary representing the HAL JSON link."""
        return self.o

    def as_link(self):
        """Returns a ``Link`` to the same resource as this link.

        This method is trivial, but is provided for symmetry with ``Document``.

        """
        return self

    @classmethod
    def from_object(cls, o, base_uri):
        """Returns a new ``Link`` based on a JSON object or array.

        Arguments:

        - ``o``: a dictionary holding the deserializated JSON for the new
                 ``Link``, or a ``list`` of such documents.
        - ``base_uri``: optional URL used as the basis when expanding
                               relative URLs in the link.

        """
        if isinstance(o, list):
            if len(o) == 1:
                return cls.from_object(o[0], base_uri)

            return map(lambda x: cls.from_object(x, base_uri), o)

        return cls(o, base_uri)

    def __iter__(self):
        yield self

    def __repr__(self):
        if hasattr(self, 'name'):
            return "<Link %s=%r>" % (self.name, self.template)
        else:
            return "<Link %r>" % self.template

    def __eq__(self, other):
        return (isinstance(other, Link) and
                self.as_object() == other.as_object())
