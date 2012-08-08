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

    .. autoattribute:: _url_base
    .. autoattribute:: _path
    .. autoattribute:: _auth
    .. autoattribute:: _parser
    .. autoattribute:: _fetched
    .. autoattribute:: _get_params

pyresto.core.Auth
----------------------

.. autoclass:: Auth

pyresto.core.AuthList
----------------------

.. autoclass:: AuthList

pyresto.core.enable_auth
------------------------

.. autofunction:: enable_auth

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

pyresto.core.PyrestoException
-----------------------------

.. autoclass:: PyrestoException

pyresto.core.PyrestoServerResponseException
-------------------------------------------

.. autoclass:: PyrestoServerResponseException

pyresto.core.PyrestoInvalidRestMethodException
----------------------------------------------

.. autoclass:: PyrestoInvalidRestMethodException

pyresto.core.PyrestoInvalidAuthTypeException
--------------------------------------------

.. autoclass:: PyrestoInvalidAuthTypeException
