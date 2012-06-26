Pyresto
=======

.. image:: https://secure.travis-ci.org/BYK/pyresto.png
    :alt: Travis CI
    :target: http://travis-ci.org/BYK/pyresto

::

    import pyresto.apis.github as GitHub

    user = GitHub.User.get('berkerpeksag')
    print 'Watchers: {0:d}'.format(sum(r.watchers for r in user.repos))


Installation
------------

To install Pyresto, simply::

    pip install pyresto


Documentation
-------------

Documentation hosted on `Read the Docs <http://pyresto.readthedocs.org/>`_.

License
-------

All files that are part of this project are covered by the following license, except where explicitly noted.

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
