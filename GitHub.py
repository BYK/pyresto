from pyresto import *

class GitHubModel(Model):
  _host='api.github.com'


class Comment(GitHubModel):
  _path = '/repos/%(__id)s/%(_id)s/comments/%(id)s'
  
  def _get_id(self):
    return self.id


class Commit(GitHubModel):
  _path = '/repos/%(__id)s/%(_id)s/commits/%(id)s'
  comments = Many(Comment, '/repos/%(___id)s/%(__id)s/commits/%(_id)s/comments')
  
  def _get_id(self):
    return self.sha

class Repo(GitHubModel):
  _path = '/repos/%(_id)s/%(id)s'
  commits = Many(Commit, '/repos/%(__id)s/%(_id)s/commits')
  comments = Many(Comment, '/repos/%(__id)s/%(_id)s/comments')
  
  def _get_id(self):
    return self.name

class User(GitHubModel):
  _path = '/users/%(id)s'
  repos = Many(Repo, '/users/%(_id)s/repos?per_page=100')
  
  def _get_id(self):
    return self.login

