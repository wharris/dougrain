Change Log
----------

0.5
===

* Compatibility with Draft 5 of the JSON HAL standard and backward
  compatibility with Draft 4 and Draft 3.
* New ``Builder``, for creating HAL resources from scratch. ``Builder`` gives
  much better performance than ``Document`` when building large resources.
* Option to force-wrap links and embedded resources in an array.
* Slight performance improvements to ``Document``'s mutation methods.

0.4
===

* Compatibility with Draft 4 of the JSON HAL standard.
* Backward compatibility with Draft 3.

0.3
===

* BUG FIX: Links now have a title property instead of a label property.
* BUG FIX: Non-templated links are no longer treated as templates.

0.2
===

* Attributes have been renamed to properties.
* The template token for CURIEs is now ``{rel}``, rather than ``{relation}``.
* Improved API for ``Document().add_link``. The second argument can now be a
  URI string or a `Document` object as well as a `Link` object. Additional
  keyword arguments are added to the link's properties.
* ``Document`` and ``Link`` objects are now iterable, yeilding themselves
  exactly once, so single and multiple links for a relation can be treated the
  same with a for loop.
  
  Example:
  ::

      >>> import dougrain
      >>> doc = dougrain.Document.empty("http://localhost/")
      >>> doc.add_link('child', "/1")
      >>> doc.links['child']
      <Link 'http://localhost/1'>
      >>> [link.href for link in doc.links['child']]
      ['/1']
      >>> doc.add_link('child', "/2")
      >>> doc.links['child']
      [<Link 'http://localhost/1'>, <Link 'http://localhost/2'>]
      >>> [link.href for link in doc.links['child']]
      ['/1', '/2']
* ``Document`` now treats link relationship types as equal if they are
  equivalent to the same URI when expanded.
  
  Example:
  ::

      >>> import dougrain
      >>> doc = dougrain.Document.empty("http://localhost/")
      >>> doc.set_curie('role', "/roles/{rel}")
      >>> doc.add_link("role:app", "/apps/1")
      >>> doc.add_link("/roles/app", "/apps/2")
      >>> doc.add_link("http://localhost/roles/app", "/apps/3")
      >>> [link.href for link in doc.links["role:app"]]
      ['/apps/1', '/apps/2', '/apps/3']
      >>> [link.href for link in doc.links["/roles/app"]]
      ['/apps/1', '/apps/2', '/apps/3']
      >>> [link.href for link in doc.links["http://localhost/roles/app"]]
      ['/apps/1', '/apps/2', '/apps/3']

0.1
===

Initial release.

