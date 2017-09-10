Examples
========

.. code-block:: python

    from grole import Grole

    app = Grole()

    @app.route('/(.*)?')
    def index(env, req):
        name = req.match.group(1) or 'World'
        return 'Hello, {}!'.format(name)

    app.run()

Run this script and then point your browser at http://localhost:1234/.

Grole also has an inbuilt simple file server which will serve all the files in a directory. Just run `grole.py` or `python -m grole`.

Further examples can be found within the examples_ folder on github.

.. _examples: https://github.com/witchard/grole/tree/master/examples
