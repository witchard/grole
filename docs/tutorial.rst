.. module:: grole

Tutorial
========

Getting started
---------------

By default, grole will run a simple static file server in the current directory. To use this simply execute `grole.py`, or run `python -m grole`.

To serve your own functions, you first need a :class:`Grole` object. The constructor accepts a `env` variable which is passed to your handler functions such that you can share state between them.

Once you have setup handler functions for your web API, you can then launch the server with :func:`Grole.run`. This takes the host and port to serve on and does not return until interrupted.

Registering routes
------------------

Routes are registered to a :class:`Grole` object by decorating a function with the :func:`Grole.route` decorator. The decorator function takes a regular expression as the path to match, an array of HTTP methods (GET, POST, etc), and whether you want this function in the API doc. Docstrings of functions in the API doc are available through `env['doc']` within the handler function.

Handling requests
-----------------

Decorated functions registered to a :class:`Grole` object with :func:`Grole.route` will be called if their associated regular expression matches that of a request (as well as the HTTP method).

A registered handler is given the following objects:

* env: The `env` dictionary that the :class:`Grole` object was constructed with
* req: A :class:`Request` object containing the full details of the request. The :class:`re.MatchObject` from the path match is also added in as `req.match`.

We now know enough to make a simple web API. An example of how to return the hex value when visiting `/<inteter>` is shown below:

.. code-block:: python

    from grole import Grole

    app = Grole()

    @app.route('/(\d+)')
    def tohex(env, req):
        return hex(int(req.match.group(1)))

    app.run()

If you need to do something `async` within your handler, e.g. access a database using aioodbc then simply declare your handler as `async` and `await` as needed.

Responding
----------

In-built python types returned by registered request handlers are automatically converted into 200 OK HTTP responses. The following mappings apply:

* bytes: Sent directly with content type text/plain
* string: Encoded as bytes and sent with content type text/plain
* others: Encoded as json and sent with content type application/json

Finer grained control of the response data can be achieved using :class:`ResponseBody` or one of it's children. These allow for overriding of the content type. The following are available:

* :class:`ResponseBody`: bytes based response
* :class:`ResponseString`: string based response
* :class:`ResponseJSON`: json encoded response
* :class:`ResponseFile`: read a file to send as response

Control of the headers in the response can be achieved by returning a :class:`Response` object. This allows for sending responses other than 200 OK, for example.

Helpers
-------

Various helper functions are provided to simplify common operations:

* :func:`serve_static`: Serve static files under a directory. Optionally provide simple directory indexes.
* :func:`serve_doc`: Serve API documentation (docstrings) of registered request handlers using a simple plain text format.
