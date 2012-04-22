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

To install Pyresto, simply: ::

    $ pip install pyresto

