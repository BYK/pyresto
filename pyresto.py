import httplib
import json
import logging
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
  _continuator = lambda x,y:None
  _parser = staticmethod(json.loads)

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
  
  @classmethod
  def _rest_call(cls, **kwargs):
    conn = cls._connection
    
    try:
      conn.request(**kwargs)
      response = conn.getresponse()
    except: #should call conn.close() on any error to allow further calls to be made
      conn.close()
      return None
    
    logging.debug('Response code: %s' % response.status)
    if response.status == 200:
      continuation_url = cls._continuator(response)
      data = cls._parser(response.read())
      if continuation_url:
        logging.debug('Found more at: ' + continuation_url)
        kwargs['url'] = continuation_url
        data += cls._rest_call(**kwargs)
      
      return data
  
  @classmethod
  def get(cls, id, **kwargs):
    kwargs.update(dict(id=quote(id)))
    path = cls._path % kwargs
    data = cls._rest_call(method='GET', url=path) or {}
    instance = cls(**data)
    instance._id = id
    instance._get_params = kwargs
    return instance


class WrappedList(list):
  def __init__(self, iterable, wrapper):
    super(self.__class__, self).__init__(iterable)
    self.__wrapper = wrapper
  
  @staticmethod
  def isdict(obj):
    return isinstance(obj, dict)
  
  def __getitem__(self, key):
    item = super(self.__class__, self).__getitem__(key)
    should_wrap = self.isdict(item) or isinstance(key, slice) and any(map(self.isdict, item))
    if should_wrap:
      item = map(self.__wrapper, item) if isinstance(key, slice) \
        else self.__wrapper(item)
      self[key] = item
    
    return item

  def __getslice__(self, i, j):
    items = super(self.__class__, self).__getslice__(i, j)
    if any(map(self.isdict, items)):
      items = map(self.__wrapper, items)
      self[i:j] = items
    return items

  def __iter__(self):
    iterator = super(self.__class__, self).__iter__()
    return (self.__wrapper(item) for item in iterator)


class Many(object):
  def __init__(self, model, path = None):
    self.__model = model
    self.__path = path or model._path
    self.__cache = {}

  def _with_owner(self, owner):
    def mapper(data):
      if isinstance(data, dict):
        instance = self.__model(**data)
        instance._id = instance._get_id()
        instance._owner = owner
        return instance
      elif isinstance(data, self.__model):
        return data
    return mapper
  
  def _get_id_dict(self, owner):
    ids = {}
    while owner:
      ids[owner.__class__.__name__.lower()] = owner._id
      owner = getattr(owner, '_owner', None)
    return ids
  
  def __get__(self, instance, owner):
    if instance not in self.__cache:
      model = self.__model
      if not instance:
        return model
      
      path_params = self._get_id_dict(instance)
      if hasattr(instance, '_get_params'):
        path_params.update(instance._get_params)
      path = self.__path % path_params
      
      logging.debug('Call many path: %s' % path)
      data = model._rest_call(method='GET', url=path) or []
      self.__cache[instance] = WrappedList(data, self._with_owner(instance))
    return self.__cache[instance]
