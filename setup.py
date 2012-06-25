#!/usr/bin/env python
# coding: utf-8

import os
import pyresto

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Taken from kennethreitz/requests/setup.py
package_directory = os.path.realpath(os.path.dirname(__file__))


def get_file_contents(file_path):
    """Get the context of the file using full path name."""
    full_path = os.path.join(package_directory, file_path)
    return open(full_path, 'r').read()

setup(
    name=pyresto.__title__,
    version=pyresto.__version__,
    description='A general REST based ORM.',
    long_description=get_file_contents('README.rst'),
    author='Burak Yiğit Kaya',
    author_email='ben@byk.im',
    url='https://github.com/BYK/pyresto',
    packages=[
        'pyresto',
        'pyresto.apis'
    ],
    license='Mozilla Public License, v. 2.0',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ),
)
