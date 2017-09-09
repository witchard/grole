#!/usr/bin/env python3

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (3, 5):
    raise NotImplementedError("Sorry, you need at least Python Python 3.5+ to use grole.")

import grole

setup(name='grole',
      version=grole.__version__,
      description='A simple asyncio based web framework',
      long_description=grole.__doc__,
      author=grole.__author__,
      author_email='witchard@hotmail.co.uk',
      url='https://github.com/witchard/grole',
      download_url='https://github.com/witchard/grole/tarball/' + grole.__version__,
      py_modules=['grole'],
      scripts=['grole.py'],
      license='MIT',
      platforms='any',
      keywords=['web', 'framework', 'asyncio', 'grole'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                  ],
     )
