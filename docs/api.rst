.. _api:

API
===

.. module:: pyresto.core

.. autoclass:: ModelBase

.. autoclass:: Model
    :exclude-members: _parser

    .. automethod:: __init__

    .. autoattribute:: _secure
    .. autoattribute:: _host
    .. autoattribute:: _path
    .. autoattribute:: _continuator
    .. autoattribute:: _parser
    .. autoattribute:: _pk
    .. autoattribute:: _fetched
    .. autoattribute:: _get_params

.. autoclass:: Relation
.. autoclass:: Many

    .. automethod:: __init__

.. autoclass:: Foreign

    .. automethod:: __init__

.. autoclass:: WrappedList
.. autoclass:: LazyList

.. autoclass:: Error
