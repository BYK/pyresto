.. _api:

API
===

.. module:: pyresto.core

pyresto.core.ModelBase
----------------------

.. autoclass:: ModelBase

pyresto.core.Model
------------------

.. autoclass:: Model
    :exclude-members: _parser

    .. automethod:: __init__

    .. autoattribute:: _secure
    .. autoattribute:: _host
    .. autoattribute:: _path
    .. autoattribute:: _parser
    .. autoattribute:: _fetched
    .. autoattribute:: _get_params

pyresto.core.Relation
----------------------

.. autoclass:: Relation

pyresto.core.Many
-----------------

.. autoclass:: Many

    .. automethod:: __init__

pyresto.core.Foreign
--------------------

.. autoclass:: Foreign

    .. automethod:: __init__

pyresto.core.WrappedList
------------------------

.. autoclass:: WrappedList

pyresto.core.LazyList
---------------------

.. autoclass:: LazyList

pyresto.core.PyrestoServerResponseException
-------------------------------------------

.. autoclass:: PyrestoServerResponseException
