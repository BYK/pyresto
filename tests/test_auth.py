# coding: utf-8

from mock import Mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyresto.core import Model
from pyresto.auth import AuthList, enable_auth, InvalidAuthTypeException


class MockModel(Model):
    _pk = 'id'


class TestAuthList(unittest.TestCase):
    def setUp(self):
        self.instance = AuthList(a=1, b=2)

    def test_item_access(self):
        self.assertEqual(self.instance['a'], 1)
        self.assertEqual(self.instance['b'], 2)

    def test_attribute_access(self):
        self.assertEqual(self.instance.a, 1)
        self.assertEqual(self.instance.b, 2)


class TestEnableAuth(unittest.TestCase):
    def setUp(self):
        self.auth_list = AuthList(a=Mock(), b=Mock())
        self.auth = enable_auth(self.auth_list, MockModel, 'a')

    def test_auth(self):
        self.auth(arg='foo')
        self.assertTrue(self.auth_list.a.called_once_with('foo'))

        self.auth('b', arg='bar')
        self.assertTrue(self.auth_list.b.called_once_with('bar'))

        with self.assertRaises(InvalidAuthTypeException):
            self.auth('c', arg='baz')
