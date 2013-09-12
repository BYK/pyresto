# coding: utf-8

from mock import Mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyresto.core import Model, Many, WrappedList, LazyList


class MockModel(Model):
    _pk = 'id'


class TestModelBase(unittest.TestCase):
    def test_defaults(self):
        self.assertIsInstance(MockModel._pk, tuple)
        self.assertEqual(MockModel._path, '/mockmodel/{id}')

        class IdlessModel(Model):
            blah = True

        with self.assertRaises(TypeError):
            IdlessModel()


class TestWrappedList(unittest.TestCase):
    def setUp(self):
        self.wrapper = Mock(side_effect=lambda d: d if isinstance(d, MockModel)
                            else MockModel(**d))
        self.list = ({'id': 1}, {'id': 2})
        self.instance = WrappedList(self.list, self.wrapper)

    def test_get_item(self):
        a = self.instance[0]
        b = self.instance[1]
        # test internal caching, this should not cause a new call
        c = self.instance[0]

        self.wrapper.assert_any_call(self.list[0])
        self.wrapper.assert_any_call(self.list[1])
        self.assertEqual(self.wrapper.call_count, 2)

    def test_get_slice(self):
        a, b = self.instance[:2]
        # test internal caching, these two should not cause new calls
        c, d = self.instance[:2]
        e = self.instance[1]

        self.wrapper.assert_any_call(self.list[0])
        self.wrapper.assert_any_call(self.list[1])
        self.assertEqual(self.wrapper.call_count, 2)

    def test_iterator(self):
        for item, orig in zip(self.instance, self.list):
            self.assertEqual(item.id, orig['id'])

        # iter items are not cached so below should cause a new call
        a = self.instance[0]
        self.assertEqual(self.wrapper.call_count, len(self.list) + 1)

        self.wrapper.reset_mock()
        a = self.instance[1]
        # iter does not care about caching so below should cause 2 new calls
        for item, orig in zip(self.instance, self.list):
            self.assertEqual(item.id, orig['id'])

        self.assertEqual(self.wrapper.call_count, len(self.list) + 1)

    def test_contains(self):
        a = self.instance[0]
        self.assertIn(a, self.instance)
        self.assertNotIn(self.list[1], self.instance)
        # the line blow implicitly checks Model.__eq__
        self.assertIn(MockModel(**self.list[1]), self.instance)


class TestLazyList(unittest.TestCase):
    def setUp(self):
        self.wrapper = Mock(side_effect=lambda d: d if isinstance(d, MockModel)
                            else MockModel(**d))
        self.list = ({'id': 1}, {'id': 2})
        self.fetcher = lambda: (self.list[:1], self.fetcher_fin)
        self.fetcher_fin = lambda: (self.list[1:], None)
        self.instance = LazyList(self.wrapper, self.fetcher)

    def test_iterator(self):
        for i in xrange(2):  # run 2 times to test consecutive calls to iter
            for item, orig in zip(self.instance, self.list):
                self.assertEqual(item.id, orig['id'])


class TestManyLazy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.list = ({'id': 1}, {'id': 2})
        cls.preprocessor = Mock(side_effect=lambda d: d)

        MockModel.lazy_many = Many(MockModel, '/many', lazy=True,
                                   preprocessor=cls.preprocessor)

    def setUp(self):
        @classmethod
        def rest_call_mock(cls, url, method='GET', fetch_all=True, **kwargs):
            self.assertEqual(method, 'GET')
            self.assertFalse(fetch_all)
            if url == '/many':
                return self.list[:1], '/many?i=1'
            else:
                return self.list[1:], None

        MockModel._rest_call = rest_call_mock
        self.instance = MockModel(id=13)

    def test_non_instance(self):
        self.assertEqual(MockModel.lazy_many, MockModel)

    def test_iterator(self):
        for item, orig in zip(self.instance.lazy_many, self.list):
            self.assertEqual(item.id, orig['id'])
            self.assertIsInstance(item, MockModel)

        self.assertEqual(self.preprocessor.call_count, 2)

    def tearDown(self):
        del MockModel._rest_call

    @classmethod
    def tearDownClass(cls):
        del MockModel.lazy_many


class TestManyList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.list = ({'id': 1}, {'id': 2})
        cls.preprocessor = Mock(side_effect=lambda d: d)

        MockModel.list_many = Many(MockModel, '/many',
                                   preprocessor=cls.preprocessor)

    def setUp(self):
        @classmethod
        def rest_call_mock(cls, url, method='GET', fetch_all=True, **kwargs):
            self.assertEqual(method, 'GET')
            self.assertTrue(fetch_all)
            if url == '/many':
                return self.list[:1], '/many?i=1'
            else:
                return self.list[1:], None

        MockModel._rest_call = rest_call_mock
        self.instance = MockModel(id=13)

    def test_non_instance(self):
        self.assertEqual(MockModel.list_many, MockModel)

    def test_iterator(self):
        for item, orig in zip(self.instance.list_many, self.list):
            self.assertEqual(item.id, orig['id'])
            self.assertIsInstance(item, MockModel)

        self.assertEqual(self.preprocessor.call_count, 1)

    def tearDown(self):
        del MockModel._rest_call

    @classmethod
    def tearDownClass(cls):
        del MockModel.list_many


class TestForeign(unittest.TestCase):
    pass


class TestModel(unittest.TestCase):
    pass
