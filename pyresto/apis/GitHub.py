# coding: utf-8

from ..core import Foreign, Many, Model
from ..helpers import link_header_continuator

class GitHubModel(Model):
    _host = 'api.github.com'
    _continuator = link_header_continuator


class Comment(GitHubModel):
    _path = '{repo.url}/comments/{id}'
    _pk = 'id'


class Commit(GitHubModel):
    _path = '{repo.url}/commits/{sha}'
    _pk = 'sha'
    comments = Many(Comment, '{commit.url}/comments?per_page=100')


class Branch(GitHubModel):
    _path = None
    _pk = 'name'
    commit = Foreign(Commit)
    commits = Many(Commit, '{repo.url}/commits?per_page=100&sha={branch._id}',
                   lazy=True)


class Tag(GitHubModel):
    _path = None
    _pk = 'name'
    commit = Foreign(Commit)


class Repo(GitHubModel):
    _path = '{user.url}/{name}'
    _pk = 'name'
    commits = Many(Commit, '{repo.url}/commits?per_page=100', lazy=True)
    comments = Many(Comment, '{repo.url}/comments?per_page=100')
    tags = Many(Tag, '{repo.url}/tags?per_page=100')
    branches = Many(Branch, '{repo.url}/branches?per_page=100')


class User(GitHubModel):
    _path = '/users/{login}'
    _pk = 'login'
    repos = Many(Repo, '{user.url}/repos?type=all&per_page=100')


# Late bindings due to circular references
Repo.contributors = Many(User, '{repo.url}/contributors?per_page=100')
Repo.owner = Foreign(User, 'owner')
Repo.watcher_list = Many(User, '{repo.url}/watchers?per_page=100')
User.follower_list = Many(User, '{user.url}/followers?per_page=100')
User.watched = Many(Repo, '{user.url}/watched?per_page=100')
