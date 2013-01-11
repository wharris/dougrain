# Dougrain

Dougrain is a Python library to help you work with the JSON varient of the
[Hypertext Application Language][halhome] as defined in the [JSON Hypermedia
API Language Internet Draft][halspec]. It uses Python objects to represent the
JSON document, so you can use it with simplejson or the json module from the
standard library.

[halhome]: http://stateless.co/hal_specification.html
[halspec]: http://tools.ietf.org/html/draft-kelly-json-hal-03

## Status

This is an pre-release version. The API may have have breaking changes in the
future.

## Installation

    $ cd dougrain
    $ pip install uritemplate
    $ python setup.py install

## Testing

    $ pip install nose
    $ nosetests

The script, `autotest`, uses watchdog to run the tests automatically whenever the source changes, which can be useful for development:

    $ pip install argcomplete
    $ pip install watchdog
    $ ./autotest

## Example

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
    ...                 "href": "http://localhost/rels/{relation}", 
    ...                 "name": "r"
    ...             }, 
    ...             "self": {
    ...                 "href": "/"
    ...             }
    ...         }
    ...     },
    ...     relative_to_url="http://localhost/")
    >>> doc.attrs['welcome']
    'Hi there!'
    >>> doc.embedded['r:post'].url()
    'http://localhost/1'
    >>> new_post = Document.empty()
    >>> new_post.set_attribute("name", "Second child")
    >>> new_post.add_link("self", doc.link("/2"))
    >>> new_post.as_object()
    {'_links': {'self': {'href': '/2'}}, 'name': 'Second child'}
    >>> doc.embed('r:post', new_post)
    >>> [post['name'] for post in doc.as_object()['_embedded']['r:post']]
    ['First child', 'Second child']

