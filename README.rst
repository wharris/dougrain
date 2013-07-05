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
have breaking changes in minor releases until version 1.0. The HAL
specification is still being developed, so Dougrain is unlikely to have a
stable API until HAL itself is stable.

Compatibility
-------------

JSON HAL drafts **3**, **4**, and **5**. Python **2.7**, **3.2**, and **3.3**.

This version conforms to `JSON Hypermedia API Language Internet Draft 5
<http://tools.ietf.org/html/draft-kelly-json-hal-05>`_,
but it can also work with JSON from
`Draft 4 <http://tools.ietf.org/html/draft-kelly-json-hal-04>`_ and
`Draft 3 <http://tools.ietf.org/html/draft-kelly-json-hal-03>`_.
The draft version can be explicitly selected when the document is constructed,
but the default behavior is for documents to automatically detect which draft
to use.

This version is tested on Python 2.7, including PyPy, Python 3.2, and
Python 3.3.

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

Example
-------

``Document.from_object`` loads HAL data from a ``dict``:

::

    >>> from dougrain import Document
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
    ...             "curies": [
    ...                 {
    ...                     "href": "http://localhost/rels/{rel}", 
    ...                     "name": "r",
    ...                     "templated": True
    ...                 }
    ...             ], 
    ...             "self": {
    ...                 "href": "/"
    ...             },
    ...             "r:post": {
    ...                 "href": "/1"
    ...             },
    ...             "r:tags": {
    ...                 "href": "/tags"
    ...             }
    ...         }
    ...     },
    ...     base_uri="http://localhost/")

``Document`` instances provide methods to interrogate the document's
properties, links, and embedded resources.

::

    >>> doc.properties['welcome']
    'Hi there!'
    >>> doc.links['r:tags'].url()
    'http://localhost/tags'
    >>> doc.embedded['r:post'].url()
    'http://localhost/1'

Link relations can be specified using CURIEs or URI references:

::

    >>> doc.links['r:tags'].url()
    'http://localhost/tags'
    >>> doc.links['/rels/tags'].url()
    'http://localhost/tags'

``Builder`` provides a lightweight API for building HAL resources from scratch.
Many of ``Builder``'s methods can be chained:

::

    >>> from dougrain import Builder
    >>> new_post = (Builder("/2").set_property('name', "Second Child")
    ...                          .add_curie('admin', "/adminrels/{rel}")
    ...                          .add_link('admin:privacy', "/2/privacy"))
    >>> import json
    >>> print(json.dumps(new_post.as_object(), indent=2))
    {
      "_links": {
        "curies": [
          {
            "href": "/adminrels/{rel}", 
            "name": "admin", 
            "templated": true
          }
        ], 
        "self": {
          "href": "/2"
        }, 
        "admin:privacy": {
          "href": "/2/privacy"
        }
      }, 
      "name": "Second Child"
    }

``Builder`` and ``Document`` can be used together. For example,
``Document.embed`` will accept a ``Builder`` instance:

::

    >>> doc.embed('r:post', new_post)
    >>> [post.properties['name'] for post in doc.embedded['/rels/post']]
    ['First child', 'Second child']

