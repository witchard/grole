Grole
=====

Grole is a python (3.5+) nano web framework based on asyncio. It's goals are to be simple, embedable (single file and standard library only) and easy to use. The authors intention is that it should support standing up quick and dirty web based APIs.

It's loosely based on bottle and flask, but unlike them does not require a WSGI capable server to handle more than one request at once. Sanic is similar, but it does not meet the embedable use-case.

A grole is a multi-spouted drinking vessel (https://en.wikipedia.org/wiki/Grole), which harks to this modules bottle/flask routes but with the ability to serve multiple drinkers at once!

Example
-------

.. code-block:: python

    from grole import Grole

    app = Grole()

    @app.route('/(.*)?')
    def index(env, req):
        name = req.match.group(1) or 'World'
        return 'Hello, {}!'.format(name)

    app.run()

Run this script and then point your browser at http://localhost:1234/.

Install
-------

Either download `grole.py` directly from github and place in your project folder, or `pip3 install grole`.

License
-------

MIT.

