#!/usr/bin/env python
# coding: utf-8

import unittest

import pyresto
import pyresto.apis.github as GitHub


class GitHubTestSuite(unittest.TestCase):
    def test_user_repos(self):
        """Expects pyresto.apis.github.User."""
        user = GitHub.User.get('berkerpeksag')
        # assertIsInstance added in 2.7.
        self.assertTrue(isinstance(user, pyresto.apis.github.User))

if __name__ == '__main__':
    unittest.main()
