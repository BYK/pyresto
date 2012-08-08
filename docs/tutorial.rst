.. _tutorial:

Tutorial
========

.. module:: pyresto

Welcome to the pyresto tutorial. This tutorial will guide you about how the
:mod:`apis.GitHub` module is implemented.


The Base
--------

Start off by creating a base model class for the service you are using which
will hold the common values such as the API host, the common model
representation using ``__repr__`` etc:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 7-14


Simple Models
-------------

Then continue with implementing simple models which does not refer to any other
model, such as the ``Comment`` model for GitHub:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 17-19


Note that we didn't define *any* attributes except for the mandatory ``_path``
and ``_pk`` attributes since pyresto automatically fills all attributes
provided by the server response. This inhibits any possible efforts to
implement client side verification though since the server already verifies all
the requests made to it, and results in simpler code. This also makes the
models "future-proof" and conforms to the best practices for "real" RESTful or
Hypermedia APIs, which many recently started to use as a term instead of "real
RESTful".


Relations
---------

After defining some "simple" models, you can start implementing models having
relations with each other:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 22-25

Note that we used the attribute name ``comments`` which will "shadow" any
attribute named "comments" sent by the server as documented in
:meth:`Model<.core.Model.__init__>`, so be wise when you are choosing your
relation names and use the ones provided by the
`service documentation <http://developer.github.com/v3/repos/commits/>`_ if
there are any.

Note that we used the :class:`Many<.core.Many>` relation here. We provided the
model class itself, which will be the class of all the items in the collection
and, the path to fetch the collection. We used ``commit.url`` in the path
format where ``commit`` will be the commit instance we are bound to, or to be
clear, the commit "resource" which we are trying to get the comments of.

Since we don't expect many comments for a given commit, we used the default
:class:`Many<.core.Many>` implementation which will result in a
:class:`WrappedList<.core.WrappedList>` instance that can be considered as a
``list``. This will cause a chain of requests when this attribute is first
accessed until all the comments are fetched and no "next" link can be extracted
from the ``Link`` header. See
:meth:`Model._continuator<.core.Model._continuator>` for more info on this.

If we were expecting lots of items to be in the collection, or an unknown
number of items in the collection, we could have used ``lazy=True`` like this:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 47-54

Using ``lazy=True`` will result in a :class:`LazyList<.core.LazyList>` type of
field on the model when accessed, which is basically a generator. So you can
iterate over it but you cannot directly access a specific element by index or
get the total length of the collection.

You can also use the :class:`Foreign<.core.Foreign>` relation to refer to
other models:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 36-39

When used in its simplest form, just like in the code above, this relation
expects the primary key value for the model it is referencing, ``Commit`` here,
to be provided by the server under the **same** name. So we expect from GitHub
API to provide the commit sha, which is the primary key for ``Commit`` models,
under the label ``commit`` when we fetch the data for a ``Tag``. When this
property is accessed, a simple :meth:`Model.get<.core.Model.get>` call is made
on the ``Commit`` model, which fetches all the data associated with the it and
puts them into a newly created model instance.


Late Bindings
-------------

Since all relation types expect the class object itself for relations, it is
not always possible to put all relation definitons inside the class definition.
For those cases, you can simply late bind the relations as follows:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 74-79


Authentication
--------------

Most services require authentication even for only fetching data so providing
means of authentication is essential. Define the possible authentication
mechanisms for the service:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 4,81-82

Make sure you use the provided authentication classes by :mod:`requests.auth`
if they suit your needs. If you still need a custom authentication class, make
sure you derive it from :class:`Auth<.core.Auth>`.

After defining the authentication methods, create a module-global function that
will set the default authentication method and credentials for all requests for
convenience:

.. literalinclude:: ../pyresto/apis/github/__init__.py
    :lines: 84-85

Above, we provide the list of methods/classes we have previously defined, the
base class for our service since all other models inherit from that and will
use the authentication defined on that, unless overridden. And we also set our
default authentication mechanism to remove the burden from the shoulders of the
users of our API library.

