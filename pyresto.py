import httplib
import logging
import json
from urllib import quote

__all__ =['Model', 'Many']

logging.getLogger().setLevel(logging.DEBUG)

class ModelBase(type):
  def __new__(cls, name, bases, attrs):
    if name == 'Model' or name == 'View':
      return super(ModelBase, cls).__new__(cls, name, bases, attrs)
    new_class = type.__new__(cls, name, bases, attrs)
    
    if not hasattr(new_class, '_path'):
      new_class._path = '/%s/%%(id)s' % quote(name.lower())

    # Create function to loop over iterable validations
    #for k, v in getattr(new_class.Meta, 'validations', {}).iteritems():
    #  if isinstance(v, (list, tuple)):
    #    new_class.Meta.validations[k] = ValidatorChain(*v)

    conn_class = httplib.HTTPSConnection if new_class._secure else httplib.HTTPConnection
    new_class._connection = conn_class(new_class._host)
    
    return new_class


class Model(object):
  __metaclass__ = ModelBase
  _secure = True

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
  
  @classmethod
  def _rest_call(cls, *args, **kwargs):
    conn = cls._connection
    conn.request(*args, **kwargs)
    response = conn.getresponse()
    logging.debug('Response code: %s' % response.status)
    if response.status == 200:
      data = response.read()
      logging.debug(data)
      return json.loads(data)
  
  @classmethod
  def get(cls, id):
    path = cls._path % dict(id=quote(id))
    data = cls._rest_call('GET', path) or {}
    instance = cls(**data)
    instance._id = id
    return instance

class Many(object):
  def __init__(self, model, path = None):
    self.__model = model
    self.__path = path or model._path
    self.__cache = None

  def _with_owner(self, owner):
    def mapper(data):
      instance = self.__model(**data)
      instance._id = instance._get_id()
      instance._owner = owner
      return instance
    return mapper
  
  def _get_id_dict(self, owner):
    ids = {}
    key = 'id'
    while owner:
      key = '_' + key
      ids[key] = owner._id
      owner = getattr(owner, '_owner', None)
    return ids
  
  def __get__(self, instance, owner):
    if self.__cache:
      return self.__cache

    model = self.__model
    if not instance:
      return model
    
    path = self.__path % self._get_id_dict(instance)
    logging.debug('Call many path: %s' % path)
    data = model._rest_call('GET', path) or []
    self.__cache = map(self._with_owner(instance), data)
    return self.__cache
