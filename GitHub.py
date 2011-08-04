import re
from pyresto import *

class GitHubModel(Model):
  _host = 'api.github.com'
  
  _link_parser = re.compile(r'\<([^\>]+)\>;\srel="(\w+)"', re.I or re.U)
  @classmethod
  def _continuator(cls, response):
    link_val = response.getheader('Link', None)
    if not link_val: return
    
    links = dict(((cls._link_parser.match(link.strip()).group(2, 1)
                     for link in link_val.split(','))))
    return links.setdefault('next', None)


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

