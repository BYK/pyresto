# coding: utf-8

"""
pyresto.core
~~~~~~~~~~~~

This module contains all core pyresto classes such as Error, Model and relation
classes.

"""

import httplib


try:
    import json
except ImportError:
    import simplejson as json
import logging
from urllib import quote


__all__ = ('Error', 'Model', 'Many', 'Foreign')


class Error(Exception):
    """Base error class for pyresto."""
    pass


class ModelBase(type):
    """
    Meta class for Model type. This class automagically creates the necessary
    _path class variable if it is not already defined. The default path pattern
    is `/ModelName/{id}`. It also generates the connection factory for the new
    model based on the _secure class variable defined in the model.

    """

    def __new__(mcs, name, bases, attrs):
        if name == 'Model':  # prevent infinite recursion
            return super(ModelBase, mcs).__new__(mcs, name, bases, attrs)
        new_class = type.__new__(mcs, name, bases, attrs)

        if not hasattr(new_class, '_path'):  # don't override if defined
            new_class._path = u'/{0}/{{1:id}}'.format(quote(name.lower()))
        else:  # otherwise make sure _path is a unicode instance
            new_class._path = unicode(new_class._path)

        if new_class._secure:
            conn_class = httplib.HTTPSConnection
        else:
            conn_class = httplib.HTTPConnection
        new_class._get_connection = classmethod(lambda c: conn_class(c._host))

        return new_class


class WrappedList(list):
    """
    Wrapped list implementation to dynamically create models as someone tries
    to access an item or a slice in the list. Returns a generator instead, when
    someone tries to iterate over the whole list.

    """

    def __init__(self, iterable, wrapper):
        super(self.__class__, self).__init__(iterable)
        self.__wrapper = wrapper

    def __getitem__(self, key):
        item = super(self.__class__, self).__getitem__(key)
        # check if we need to wrap the item, or if this is a slice, then check
        # if we need to wrap any item in the slice
        should_wrap = (isinstance(item, dict) or isinstance(key, slice) and
                       any(isinstance(it, dict) for it in item))

        if should_wrap:
            item = ([self.__wrapper(_) for _ in item]
                    if isinstance(key, slice) else self.__wrapper(item))

            self[key] = item  # cache wrapped item/slice

        return item

    def __getslice__(self, i, j):
        # We need this implementation for backwards compatibility.
        items = super(self.__class__, self).__getslice__(i, j)
        if any(isinstance(it, dict) for it in items):
            items = [self.__wrapper(_) for _ in items]
            self[i:j] = items  # cache wrapped slice
        return items

    def __iter__(self):
        # Call the base __iter__ to avoid inifnite recursion and then simply
        # return an iterator.
        iterator = super(self.__class__, self).__iter__()
        return (self.__wrapper(item) for item in iterator)

    def __contains__(self, item):
        # Not very performant but necessary to use Model instances as operands
        # for the in operator.
        return item in iter(self)


class LazyList(object):
    """
    Lazy list implementation for continuous iteration over very large lists
    such as commits in a large repository. This is essentially a chained and
    structured generator. No caching and memoization at all since the intended
    usage is for small number of iterations.

    """

    def __init__(self, wrapper, fetcher):
        self.__wrapper = wrapper
        self.__fetcher = fetcher

    def __iter__(self):
        fetcher = self.__fetcher
        while fetcher:
            # fetcher is stored locally to prevent interference between
            # possible multiple iterations going at once
            data, fetcher = fetcher()  # this part never gets hit if the below
            # loop is not exhausted.
            for item in data:
                yield self.__wrapper(item)


class Relation(object):
    """Base class for all relation types."""
    pass


class Many(Relation):
    """
    Class for 'many' relation type which is essentially a collection of a
    certain model. Needs a base model for the collection and a path to get
    the collection from. Falls back to provided model's path if none provided.

    Use lazy=true if the number of items in the collection will be uncertain or
    very large. This will make the property a generator instead of a list.

    """

    def __init__(self, model, path=None, lazy=False):
        self.__model = model
        self.__path = unicode(path) or model._path  # ensure unicode
        self.__lazy = lazy
        self.__cache = dict()

    def _with_owner(self, owner):
        """
        A function factory method which returns a mapping/wrapping function.
        The returned function creates a new instance of the model the relation
        is defined by, sets its owner and "automatically fetched" internal flag
        and returns it.

        """

        def mapper(data):
            if isinstance(data, dict):
                instance = self.__model(**data)
                # set auto fetching true for man fields
                # which usually contain a summary
                instance._auto_fetch = True
                instance._pyresto_owner = owner
                return instance
            elif isinstance(data, self.__model):
                return data

        return mapper

    def __make_fetcher(self, url):
        """
        A function factory method which creates a simple fetcher function for
        the model, used by the model internally. The "_rest_call" method
        defined on the models is expected to return the data and a continuation
        URL if there is any. This method generates a bound, fetcher function
        that calls the internal "_rest_call" function on the method, and
        processes its results to confront the requirements explained above.

        """

        def fetcher():
            data, new_url = self.__model._rest_call(method='GET',
                                                    url=url,
                                                    fetch_all=False)
            # Note the fetch_all=False in the call above, since this method is
            # intended for iterative LazyList calls.
            if not data:
                data = []

            new_fetcher = self.__make_fetcher(new_url) if new_url else None
            return data, new_fetcher

        return fetcher

    def __get__(self, instance, owner):
        # This method is called whenever a field defined as Many is tried to
        # be accessed. There is also another usage which lacks an object
        # instance in which case this simply returns the Model class then.
        if not instance:
            return self.__model

        if instance not in self.__cache:
            model = self.__model

            # Get the necessary dict object collected from the chain of Models
            # to properly populate the collection path
            path_params = instance._parents
            if hasattr(instance, '_get_params'):
                path_params.update(instance._get_params)
            path = self.__path.format(**path_params)

            if self.__lazy:
                self.__cache[instance] = LazyList(self._with_owner(instance),
                                                  self.__make_fetcher(path))
            else:
                data, next_url = model._rest_call(method='GET', url=path)
                self.__cache[instance] =\
                            WrappedList(data or [], self._with_owner(instance))
        return self.__cache[instance]


class Foreign(Relation):
    """
    Class for 'foreign' relation type which is essentially a reference to a
    certain model. Needs a base model for obvious reasons. The constructor
    accepts optional key_property and key_extractor parameters.

    key_property is the name of the property on the base model to get the id of
    the foreign model. key_extractor is the function to extract the id of the
    foreign model from the provided base model instance. This arguments is
    provided to allow possible complex id extraction operations for foreign
    fields.

    """

    def __init__(self, model, key_property=None, key_extractor=None):
        self.__model = model
        if not key_property:
            key_property = model.__name__.lower()
        model_pk = model._pk
        self.__key_extractor = (key_extractor if key_extractor else
            lambda x: dict(model_pk=getattr(x, '__' + key_property)[model_pk]))

        self.__cache = dict()

    def __get__(self, instance, owner):
        # Please see Many.__get__ for more info on this method.
        if not instance:
            return self.__model

        if instance not in self.__cache:
            keys = instance._parents
            keys.update(self.__key_extractor(instance))
            pk = keys.pop(self.__model._pk)
            self.__cache[instance] = self.__model.get(pk, **keys)

        return self.__cache[instance]


class Model(object):
    """
    The base model class where every data model using pyresto should be
    inherited from. Uses ModelBase as its metaclass for various reasons
    explained in ModelBase.

    _secure class variable determines wheter the HTTPS or the HTTP protocol
    should be used for requests made to the REST server. Defaults to True
    meaning HTTPS will be used.

    _host is the hostname for the API endpoint for the Model which is used in
    conjunction with the _secure property to generate a bound HTTP request
    factory at the time of class definition. See ModelBase for implementation.

    _path is the path to be used while fetching the instance from the server.
    It is a format string using the new format notation defined for str.format
    method. The primary key will be passed under the same name defined in the
    _pk property and any other named parameters passed to the Model.get method
    or the class constructor are available to this string for formatting.

    _continuator is a class method which receives the class object (like a
    regular class method) and the request made to the server. This method is
    expected to return a continuation URL for the fetched resource, if there is
    any (like the next page's URL for paginated content) and None otherwise.
    Defaults to a dummy function which always returns None.

    _parser is a class method which receives the class object and the body text
    of the server response to be parsed. It is expected to return a dictionary
    object having the properties of the related model. Defaults to a
    "staticazed" version of json.loads so it is not necessary to override it if
    the response type is valid JSON.

    _pk is a class variable where the attribute name for the primary key of the
    model is stored as a string. This property is required and not providing a
    default is intentional to force developers to explicitly define it on every
    model class.

    _fetched is an instance variable which is used to determine if the model
    instance is filled from the server or not. It can be modified for certain
    usages but this is not advised. If _fetched is false when an attribute not
    in the class dictionary tried to be accessed, the __fetch method is called
    before raising an AttributeError.

    _get_params is an instance variable which holds the additional named get
    parameters provided to the Model.get class method to fetch the instance. It
    is used internally by the relation classes to have more info about the
    current model instance while fetching its related resources.


    """
    __metaclass__ = ModelBase
    _secure = True
    _continuator = lambda x, y: None
    _parser = staticmethod(json.loads)
    _fetched = False
    _get_params = dict()
    __ids = None

    def __init__(self, **kwargs):
        """
        Constructor for model instances. All named parameters passed to this
        method are bound to the newly created instance. Any property names
        provided at this level which are interfering with the predefined class
        relations (especially for Foreign fields) prepended "__" to avoid
        conflicts and to be used by the related relation class. So for instance
        if your class has "father = Foreign(Father)" and "father" is provided
        at the level of instantiation, its value is saved under __father to be
        used by the Foreign relationship class as the id of the foreign model.

        Constructor also tries to populate the _current_path instance variable
        by formatting the Model._path using the properties provided.

        """
        self.__dict__.update(kwargs)

        cls = self.__class__
        overlaps = set(cls.__dict__) & set(kwargs)

        for item in overlaps:
            if issubclass(getattr(cls, item), Model):
                self.__dict__['__' + item] = self.__dict__.pop(item)

        try:
            self._current_path = self._path and (
                self._path.format(**self.__dict__))
        except KeyError:
            self._current_path = None

    @property
    def _id(self):
        """A property that returns the model instance's primary key value."""
        return getattr(self, self._pk)

    @property
    def _parents(self):
        """
        A property that returns a look-up dictionary for all parents of
        the current instance. Uses lowercased class names for keys and the
        instance references as the values.

        """
        if self.__ids is None:
            self.__ids = dict()
            owner = self
            while owner:
                self.__ids[owner.__class__.__name__.lower()] = owner
                owner = getattr(owner, '_pyresto_owner', None)

        return self.__ids

    @classmethod
    def _rest_call(cls, fetch_all=True, **kwargs):
        conn = cls._get_connection()
        response = None
        try:
            conn.request(**kwargs)
            response = conn.getresponse()
        except Exception as e:
            # should call conn.close() on any error
            # to allow further calls to be made
            conn.close()
            if isinstance(e, httplib.BadStatusLine):
                if not response:  # retry
                    return cls._rest_call(fetch_all, **kwargs)
            else:
                raise e

        if 200 <= response.status < 300:
            continuation_url = cls._continuator(response)
            encoding = response.getheader('content-type', '').split('charset=')
            encoding = encoding[1] if len(encoding) > 1 else 'utf-8'
            response_data = unicode(response.read(), encoding, 'replace')
            data = cls._parser(response_data) if response_data else None
            if continuation_url:
                logging.debug('Found more at: %s', continuation_url)
                if fetch_all:
                    kwargs['url'] = continuation_url
                    data += cls._rest_call(**kwargs)[0]
                else:
                    return data, continuation_url
            return data, None
        else:
            conn.close()
            logging.error("URL returned HTTP %d: %s", response.status, kwargs)
            raise Error("Server response not OK. Response code: %d" %
                        response.status)

    def __fetch(self):
        # if we don't have a path then we cannot fetch anything since we don't
        # know the address of the resource.
        if not self._current_path:
            self._fetched = True
            return

        data, next_url = self._rest_call(method='GET', url=self._current_path)
        if next_url:
            self._current_path = next_url

        if data:
            self.__dict__.update(data)
            self._fetched = True

    def __getattr__(self, name):
        if self._fetched:  # if we fetched and still don't have it, no luck!
            raise AttributeError
        self.__fetch()
        return getattr(self, name)  # try again after fetching

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._id == other._id

    def __repr__(self):
        if self._current_path:
            descriptor = self._current_path
        else:
            descriptor = ' - {0}: {1}'.format(self._pk, self._id)

        return '<Pyresto.Model.{0} [{1}{2}]>'.format(self.__class__.__name__,
                                                     self._host, descriptor)

    @classmethod
    def get(cls, model_id, **kwargs):
        kwargs[cls._pk] = model_id
        path = cls._path.format(**kwargs)
        data = cls._rest_call(method='GET', url=path)[0]

        if not data:
            return

        instance = cls(**data)
        instance._get_params = kwargs
        instance._fetched = True
        return instance
