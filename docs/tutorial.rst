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
representation using ``__repr__`` etc::

    class GitHubModel(Model):
        _host = 'api.github.com'

        def __repr__(self):
            if self.url:
                descriptor = self.url
            else:
                descriptor = ' - {0}: {1}'.format(self._pk, self._id)

            return '<GitHub.{0} [{1}]>'.format(self.__class__.__name__, descriptor)


Simple Models
-------------

Then continue with implementing simple models which does not refer to any other
model, such as the ``Comment`` model for GitHub::

    class Comment(GitHubModel):
        _path = '{repo.url}/comments/{id}'
        _pk = 'id'


Note that we didn't define *any* attributes except for the mandatory ``_path``
and ``_pk`` attributes since pyresto automatically fills all attributes
provided by the server response. This inhibits any possible efforts to
implement client side verification though since the server already verifies all
the requests made to it, but allows much simpler code. This also makes the
models "future-proof" and conforms to the best practices for "real" RESTful or
Hypermedia APIs, which many recently started to use as a term instead of "real
RESTful".


Relations
---------

After defining some "simple" models, you can start implementing models having
relations with each other::

    class Commit(GitHubModel):
        _path = '{repo.url}/commits/{sha}'
        _pk = 'sha'
        comments = Many(Comment, '{commit.url}/comments?per_page=100')

Note that we used the attribute name ``comments`` which will "shadow" any
attribute named "comments" sent by the server as documented in
:meth:`Model<.core.Model.__init__>`, so be wise when you are choosing your
relation names and use the ones provided by the
`service documentation <http://developer.github.com/v3/repos/commits/>` if
there are any.

Note that we used the :class:`Many<.core.Many>` relation here. We provided the
model class itself, which will be the class of all the items in the collection
and the path to fetch the collection. We used ``commit.url`` in the path format
where ``commit`` will be the commit instance we are bound to, or to be clear,
the commit "resource" which we are trying to get the comments of.

Since we don't expect many comments for a given commit, we used the default
:class:`Many<.core.Many>` implementation which will result in a class which
simply is a ``list`` derivative. This will cause a chain of requests when this
attribute is first accessed until all the comments are fetched and no "next"
link can be extracted from the ``Link`` header. See
:meth:`Model._continuator<.core.Model._continuator>` for more info about this.

If we were expecting lots of items in the collection, or an unknown number of
items in the collection, we could have used ``lazy=True`` like this::

    class Repo(GitHubModel):
        _path = '{user.url}/{name}'
        _pk = 'name'
        commits = Many(Commit, '{repo.url}/commits?per_page=100', lazy=True)
        comments = Many(Comment, '{repo.url}/comments?per_page=100')
        tags = Many(Tag, '{repo.url}/tags?per_page=100')
        branches = Many(Branch, '{repo.url}/branches?per_page=100')

Using ``lazy=True`` will result in a :class:`LazyList<.core.LazyList>` type of
field on the model when accessed which is basically a generator so you can
iterate over it but you cannot directly access a specific element by index or
get the total length of the collection.

You can also use the :class:`Foreign<.core.Foreign>` relation to reference
other models::

    class Tag(GitHubModel):
        _path = None
        _pk = 'name'
        commit = Foreign(Commit)

When used as its simples form, just like in the code above, this relation
expects the primary key value for the model it is referencing, ``Commit`` here,
to be provided by the server under the **same** name. So we expect from GitHub
API to provide the commit sha, which is the primary key for ``Commit`` models
uner the label ``commit`` when we fetch the data for a ``Tag``. When this
property is accessed, a simple :meth:`Model.get<.core.Model.get>` call is made
on the ``Commit`` model, which fetches all the data associated with the commit
whose SHA hash is provided.


Late Bindings
-------------

Since all relation types expect the class object itself for relations, it is
not always possible to put all relation definitons inside the class definition.
For those cases, you can simply late bind the relations as follows::

    # Late bindings due to circular references
    Repo.contributors = Many(User, '{repo.url}/contributors?per_page=100')
    Repo.owner = Foreign(User, 'owner')
    Repo.watcher_list = Many(User, '{repo.url}/watchers?per_page=100')
    User.follower_list = Many(User, '{user.url}/followers?per_page=100')
    User.watched = Many(Repo, '{user.url}/watched?per_page=100')
