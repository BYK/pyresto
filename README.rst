Pyresto
=======

::

    import pyresto.apis.GitHub as GitHub
    import operator

    user = GitHub.User.get('berkerpeksag')
    all_commits = reduce(operator.add, [r.commits for r in user.repos], [])
    own_commits = [c for c in all_commits if c['committer'] and c['committer']['login'] == user.login]
    len(own_commits)  # 508

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

