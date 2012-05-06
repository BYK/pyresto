#!/usr/bin/env python
# coding: utf-8

import unittest

import pyresto
import pyresto.apis.GitHub as GitHub


class GitHubTestSuite(unittest.TestCase):
    def test_user_repos(self):
        """Expects pyresto.apis.GitHub.User."""
        user = GitHub.User.get('berkerpeksag')
        self.assertIsInstance(user, pyresto.apis.GitHub.User)

if __name__ == '__main__':
    unittest.main()
