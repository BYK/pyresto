Pyresto
=======

[![Travis CI](https://secure.travis-ci.org/BYK/pyresto.png)](http://travis-ci.org/BYK/pyresto)

```python
import pyresto.apis.GitHub as GitHub

user = GitHub.User.get('berkerpeksag')
print 'Watchers: {0:d}'.format(sum(r.watchers for r in user.repos))
```

Installation
------------

To install Pyresto, simply:

```shell
pip install pyresto
```

Documentation
-------------

Documentation hosted on [Read the Docs](http://pyresto.readthedocs.org/).

License
-------

All files that are part of this project are covered by the following license, except where explicitly noted.

> This Source Code Form is subject to the terms of the Mozilla Public
> License, v. 2.0. If a copy of the MPL was not distributed with this
> file, You can obtain one at http://mozilla.org/MPL/2.0/.

