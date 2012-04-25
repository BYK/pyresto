Pyresto
=======

::

    import pyresto.apis.GitHub as GitHub

    user = GitHub.User.get('berkerpeksag')
    sum(r.watchers for r in user.repos)  # 332

Installation
------------

To install Pyresto, simply::

    $ pip install pyresto


License
-------

All files that are part of this project are covered by the following license, except where explicitly noted.::

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

