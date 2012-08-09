# coding: utf-8

from ...core import Foreign, Many, Model, AuthList, enable_auth
from requests.auth import HTTPBasicAuth


class GitHubModel(Model):
    _url_base = 'https://api.github.com'

    def __repr__(self):
        descriptor = getattr(self, "url",
                             '`{0}`: {1}'.format(self._pk, self._id))

        return '<GitHub.{0} [{1}]>'.format(self.__class__.__name__, descriptor)


class Comment(GitHubModel):
    _path = '/repos/{user}/{repo}/comments/{id}'
    _pk = 'id'


class Commit(GitHubModel):
    _path = '/repos/{user}/{repo}/commits/{sha}'
    _pk = 'sha'
    comments = Many(Comment, '{commit.url}/comments?per_page=100')


class Branch(GitHubModel):
    _path = '/repos/{user}/{repo}/branches/{name}'
    _pk = 'name'
    commit = Foreign(Commit)
    commits = Many(Commit, '{repo.url}/commits?per_page=100&sha={branch._id}',
                   lazy=True)


class Tag(GitHubModel):
    _path = '/repos/{user}/{repo}/tags/{id}'
    _pk = 'name'
    commit = Foreign(Commit)


class Key(GitHubModel):
    _path = '/user/keys/{id}'
    _pk = 'id'


class Repo(GitHubModel):
    _path = '/repos/{user}/{name}'
    _pk = 'name'
    commits = Many(Commit, '{repo.url}/commits?per_page=100', lazy=True)
    comments = Many(Comment, '{repo.url}/comments?per_page=100')
    tags = Many(Tag, '{repo.url}/tags?per_page=100')
    branches = Many(Branch, '{repo.url}/branches?per_page=100')
    keys = Many(Key, '{repo.url}/keys?per_page=100')


class User(GitHubModel):
    _path = '/users/{login}'
    _pk = 'login'

    repos = Many(Repo, '{user.url}/repos?type=all&per_page=100')
    keys = Many(Key, '/user/keys?per_page=100')


class Me(User):
    _path = '/user'
    repos = Many(Repo, '/user/repos?type=all&per_page=100')

    @classmethod
    def get(cls, **kwargs):
        return super(Me, cls).get(None, **kwargs)


# Late bindings due to circular references
Repo.contributors = Many(User, '{repo.url}/contributors?per_page=100')
Repo.owner = Foreign(User, 'owner')
Repo.watcher_list = Many(User, '{repo.url}/watchers?per_page=100')
User.follower_list = Many(User, '{user.url}/followers?per_page=100')
User.watched = Many(Repo, '{user.url}/watched?per_page=100')

# Define authentication methods
auths = AuthList(basic=HTTPBasicAuth)

# Enable and publish global authentication
auth = enable_auth(auths, GitHubModel, 'basic')
