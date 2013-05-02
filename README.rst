Dougrain
========

Dougrain is a Python library to help you work with the JSON variant of the
`Hypertext Application Language <http://stateless.co/hal_specification.html>`_
(HAL). It uses Python objects to represent the JSON document, so you can use
it with whichever JSON library you prefer.

Status
------

.. image:: https://travis-ci.org/wharris/dougrain.png?branch=master
   :alt: build status
   :target: https://travis-ci.org/wharris/dougrain

This is a pre-release version. It usually works pretty well, but the API may
have have breaking changes in minor releases until version 1.0. The HAL
specification is still being developed, so Dougrain is unlikely to have a
stable API until HAL itself is stable.

Compatibility
-------------

Drafts **3** and **4**.

This version is conforms to `JSON Hypermedia API Language Internet Draft 4
<http://tools.ietf.org/html/draft-kelly-json-hal-04>`_, but can also parse and
output JSON from
`Draft 3 <http://tools.ietf.org/html/draft-kelly-json-hal-03>`_.
The draft version can be explicitly selected when the document is constructed,
but the default behavior is for documents to automatically detect which draft
to use.

Installation
------------

You'll probably need to use sudo on the install commands, or run in a
virtualenv.

The easiest way to install the current release is to use pip:

::

    $ pip install dougrain

You can install a local copy of the source in the usual way:

::

    $ cd dougrain
    $ pip install -r requirements.txt
    $ python setup.py install

Testing
-------

The easiest way to run the tests is to use nose, so install nose if you don't
already have it:

::

    $ pip install nose

Then run nose:

::

    $ nosetests

Example
-------

::

    >>> from dougrain import Document
    >>> import json
    >>> doc = Document.from_object(
    ...     {
    ...         "_embedded": {
    ...             "r:post": {
    ...                 "_links": {
    ...                     "self": {
    ...                         "href": "/1"
    ...                     }, 
    ...                     "r:site": {
    ...                         "href": "/"
    ...                     }
    ...                 }, 
    ...                 "name": "First child"
    ...             }
    ...         }, 
    ...         "welcome": "Hi there!", 
    ...         "_links": {
    ...             "curie": {
    ...                 "href": "http://localhost/rels/{rel}", 
    ...                 "name": "r"
    ...             }, 
    ...             "self": {
    ...                 "href": "/"
    ...             }
    ...         }
    ...     },
    ...     relative_to_url="http://localhost/")
    >>> doc.properties['welcome']
    'Hi there!'
    >>> doc.embedded['r:post'].url()
    'http://localhost/1'
    >>> new_post = Document.empty()
    >>> new_post.set_property("name", "Second child")
    >>> new_post.add_link("self", "/2")
    >>> new_post.as_object()
    {'_links': {'self': {'href': '/2'}}, 'name': 'Second child'}
    >>> doc.embed('r:post', new_post)
    >>> [post['name'] for post in doc.as_object()['_embedded']['r:post']]
    ['First child', 'Second child']

