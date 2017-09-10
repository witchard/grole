.. Grole documentation master file, created by
   sphinx-quickstart on Sun Sep 10 20:07:04 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Grole's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   tutorial
   examples
   api

Grole is a python (3.5+) nano web framework based on asyncio. It's goals are to be simple, embedable (single file and standard library only) and easy to use. The authors intention is that it should support standing up quick and dirty web based APIs.

It's loosely based on bottle and flask, but unlike them does not require a WSGI capable server to handle more than one request at once. Sanic is similar, but it does not meet the embedable use-case.

A grole is a multi-spouted drinking vessel (https://en.wikipedia.org/wiki/Grole), which harks to this modules bottle/flask routes but with the ability to serve multiple drinkers at once!

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
