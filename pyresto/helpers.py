# coding: utf-8

"""
pyresto.helpers
~~~~~~~~~~~~

This module contains some helpers which pyresto does not use directly but may
be useful when defining APIs.

"""

import re


# An HTTP link header parser to be used in link_header_continuator
link_header_regexp = re.compile(r'\<([^\>]+)\>;\srel="(\w+)"', re.I | re.U)


@classmethod
def link_header_continuator(cls, response):
    """
    A collection continuator function that can be used on the derived models
    as their _continuator method which parses the standard HTTP Link header and
    returns the url provided under the name "next" for continuation.

    """
    link_val = response.getheader('Link', None)
    if not link_val:
        return

    links = dict(((link_header_regexp.match(link.strip()).group(2, 1)
        for link in link_val.split(','))))
    return links.setdefault('next', None)
