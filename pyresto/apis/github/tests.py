#!/usr/bin/env python
# coding: utf-8

try:
    import unittest2 as unittest
except:
    import unittest


class GitHubTestCase(unittest.TestCase):
    @classmethod
    def cleanup_modules(cls):
        """
        Removes all pyresto related modules from module cache to force reload
        using the httplib stub. Ugly, but effective.
        """
        import sys
        for module in sys.modules.keys():
            if module.find('pyresto') == 0:
                del sys.modules[module]

    @classmethod
    def setUpClass(cls):
        cls.cleanup_modules()
        from pyresto.mocks import httplib
        cls.httplib = httplib
        httplib.stub('pyresto.httplib')

        from pyresto.apis import github as GitHub
        cls.api = GitHub

    @classmethod
    def tearDownClass(cls):
        #cls.cleanup_modules()
        cls.httplib.restore('pyresto.httplib')
        del cls.api


class GitHubTestSuite(GitHubTestCase):
    def test_user_repos(self):
        """Expects pyresto.apis.github.User."""
        test = self

        def response(self, path, method, body, headers):
            test.assertEqual(path, "/users/berkerpeksag", "Ensure path")
            test.assertEqual(method, "GET", "Ensure method")
            return (200,
                    {'content-type': 'application/javascript; charset=utf-8'},
                    '{"login": "berkerpeksag"}')

        self.httplib.HTTPSConnection._callback = response
        user = self.api.User.get('berkerpeksag')
        self.assertEqual(user._id, 'berkerpeksag')

if __name__ == '__main__':
    unittest.main()
