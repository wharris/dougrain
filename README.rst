Dougrain
========

Dougrain is a Python library to help you work with the JSON variant of the
`Hypertext Application Language <http://stateless.co/hal_specification.html>`_.
It uses Python objects to represent the JSON document, so you can use it with
whichever JSON library you prefer.

Status
------

.. image:: https://travis-ci.org/wharris/dougrain.png?branch=master
   :alt: build status
   :target: https://travis-ci.org/wharris/dougrain

This is a pre-release version. The API may have have breaking changes
in minor version releases until version 1.0.

Compatibility
-------------

This version is conforms to `JSON Hypermedia API Language Internet Draft 4
<http://tools.ietf.org/html/draft-kelly-json-hal-04>`_, but can also parse and
output JSON from
`Draft 3 <http://tools.ietf.org/html/draft-kelly-json-hal-03>`_.
The draft version can be explicitly selected when the document is constructed,
but the default behavior is for documents to automatically detect which draft
to use.

Installation
------------

Via pip:

::

    $ pip install dougrain

From source:

::

    $ cd dougrain
    $ pip install -r requirements.txt
    $ python setup.py install

You'll probably need to sudo or run in a virtualenv.

Testing
-------

::

    $ pip install nose
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

