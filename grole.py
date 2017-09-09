#!/usr/bin/env python3
"""
Grole is a python (3.5+) nano web framework based on asyncio. It's goals are to be simple, embedable (single file and standard library only) and easy to use.
"""
import asyncio
import socket
import json
import re
import urllib
import traceback
import inspect
import io
import mimetypes
import pathlib
import html
from collections import defaultdict

__author__ = 'witchard'
__version__ = '0.1.0'

class Request:
    """
    Represents a single HTTP request

    The read method parses a request. The following members are filled in
    with the details:
      method   The request method
      location The request location as it is sent
      path     The unescaped path part of the location
      query    The query string part of the location (if present)
      version  The request version, e.g. HTTP/1.1
      headers  Dictionary of headers from the request
      data     Raw data from the request body

    The body() and json() methods  are provided to access the body in a more
    sane manner.
    """

    async def read(self, reader):
        """
        Parses HTTP request into member variables
        """
        start_line = await self._readline(reader)
        self.method, self.location, self.version = start_line.decode().split()
        path_query = self.location.split('?', 1)
        self.path = urllib.parse.unquote(path_query[0])
        self.query = {}
        if len(path_query) > 1:
            for q in path_query[1].split('&'):
                try:
                    k, v = q.split('=', 1)
                    self.query[k] = v
                except ValueError:
                    self.query[q] = None
        self.headers = {}
        while True:
            header_raw = await self._readline(reader)
            if header_raw.strip() == b'':
                break
            header = header_raw.decode().split(':', 1)
            self.headers[header[0]] = header[1].strip()

        # TODO implement chunked handling
        self.data = b''
        await self._buffer_body(reader)

    async def _readline(self, reader):
        """
        Readline helper
        """
        ret = await reader.readline()
        if len(ret) == 0 and reader.at_eof():
            raise EOFError()
        return ret

    async def _buffer_body(self, reader):
        """
        Buffers the body of the request
        """
        remaining = int(self.headers.get('Content-Length', 0))
        if remaining > 0:
            try:
                self.data = await reader.readexactly(remaining)
            except asyncio.IncompleteReadError:
                raise EOFError()

    def body(self):
        """
        Decodes body as string
        """
        return self.data.decode()

    def json(self):
        """
        Decodes json object from the body
        """
        return json.loads(self.body())

class ResponseBody:
    """
    Response body from a byte string
    """
    def __init__(self, data=b'', content_type='text/plain'):
        """
        Initialise object, data is the data to send
        """
        self._headers = {'Content-Length': len(data),
                         'Content-Type': content_type}
        self._data = data

    def set_headers(self, headers):
        """
        Merge internal headers into the passed in dictionary
        """
        headers.update(self._headers)

    async def write(self, writer):
        """
        Write out the data
        """
        writer.write(self._data)
        await writer.drain()

class ResponseString(ResponseBody):
    """
    Response body from a string
    """
    def __init__(self, data='', content_type='text/plain'):
        super().__init__(data.encode(), content_type)

class ResponseJSON(ResponseString):
    """
    Response body encoded in json
    """
    def __init__(self, data='', content_type='application/json'):
        super().__init__(json.dumps(data), content_type)

class ResponseFile(ResponseBody):
    """
    Respond with a file

    Content type is guessed if not provided
    """
    def __init__(self, filename, content_type=None):
        if content_type == None:
            content_type = mimetypes.guess_type(filename)[0]
        self._file = io.FileIO(filename)
        self._headers = {'Transfer-Encoding': 'chunked',
                         'Content-Type': content_type}

    async def write(self, writer):
        while True:
            data = self._file.read(io.DEFAULT_BUFFER_SIZE)
            header = format(len(data), 'x') + '\r\n'
            writer.write(header.encode())
            writer.write(data)
            writer.write(b'\r\n')
            await writer.drain()
            if len(data) == 0:
                return # EOF

class Response:
    """
    Represents a single HTTP response

    The write method sends the response. The following members are used to
    construct it:
      version  The response version, default HTTP/1.1
      code     The response code, default 200
      reason   The response reason, default OK
      headers  Dictionary of response headers, default is a Server header
      data     Object to send e.g. ResponseBody / ResponseJSON
    """
    def __init__(self, data=None, code=200, reason='OK', headers={},
                 version='HTTP/1.1'):
        self.version = version
        self.code = code
        self.reason = reason
        self.data = self._create_body(data)
        self.headers = {'Server': 'grole/' + __version__}
        self.data.set_headers(self.headers) # Update headers from data
        self.headers.update(headers) # Update headers from user

    async def write(self, writer):
        start_line = '{} {} {}\r\n'.format(self.version, self.code, self.reason)
        headers = ['{}: {}'.format(x[0], x[1]) for x in self.headers.items()] 
        header = start_line + '\r\n'.join(headers) + '\r\n\r\n'
        writer.write(header.encode())
        await writer.drain()
        await self.data.write(writer)

    def _create_body(self, data):
        if isinstance(data, ResponseBody):
            return data
        elif data is None:
            return ResponseBody()
        elif isinstance(data, bytes):
            return ResponseBody(data)
        elif isinstance(data, str):
            return ResponseString(data)
        else:
            return ResponseJSON(data)

def serve_static(app, base_url, base_path, index=False):
    """
    Serve a directory statically

    Parameters:
        app - Grole application object
        base_url - Base URL to serve from, e.g. /static
        base_path - Base path to look for files in
        index - Provide simple directory indexes if True
    """
    @app.route(base_url + '/(.*)')
    def serve(env, req):
        """
        Static files
        """
        base = pathlib.Path(base_path).resolve()
        path = (base / req.match.group(1)).resolve()

        # Don't let bad paths through
        if base == path or base in path.parents:
            if path.is_file():
                return ResponseFile(str(path))
            if index and path.is_dir():
                if base == path:
                    ret = ''
                else:
                    ret = '<a href="../">../</a><br/>\r\n'
                for item in path.iterdir():
                    name = item.parts[-1]
                    if item.is_dir():
                        name += '/'
                    ret += '<a href="{}">{}</a><br/>\r\n'.format(urllib.parse.quote(name), html.escape(name))
                ret = ResponseString(ret, 'text/html')
                return ret

        return Response(None, 404, 'Not Found')

def serve_doc(app, url):
    """
    Serve API documentation

    Parameters:
        app - Grole application object
        url - URL to serve at
    """
    @app.route(url, doc=False)
    def index(env, req):
        ret = ''
        for d in env['doc']:
            ret += 'URL: {url}, supported methods: {methods}{doc}\n'.format(**d)
        return ret

class Grole:
    """
    A Grole Webserver
    
    For example:
        app = Grole()
        @app.route('/')
        def index(env, req):
          return 'Hello, World!'
        app.run()
    """
    def __init__(self, env={}):
        """
        Initialise a server

        Parameters:
            env - Passed to request handlers to provide shared state
            Note, env by default contains doc which is populated from
            registered route docstrings.
        """
        self._handlers = defaultdict(list)
        self.env = {'doc': []}
        self.env.update(env)

    def route(self, path_regex, methods=['GET'], doc=True):
        """
        Decorator to register a handler

        Parameters:
            path_regex - Request path regex to match against for running the handler
            methods - HTTP methods to use this handler for
            doc - Add to internal doc structure
        """
        def register_func(func):
            """
            Decorator implementation
            """
            if doc:
                self.env['doc'].append({'url': path_regex, 'methods': ', '.join(methods), 'doc': func.__doc__})
            for method in methods:
                self._handlers[method].append((re.compile(path_regex), func))
            return func # Return the original function
        return register_func # Decorator

    async def handle(self, reader, writer):
        """
        Handle a single TCP connection

        Parses requests, finds appropriate handlers and returns responses
        """
        peer = writer.get_extra_info('peername')
        print('New connection from {}'.format(peer))
        try:
            # Loop handling requests
            while True:
                # Read the request
                req = Request()
                await req.read(reader)

                # Find and execute handler
                res = None
                for path_regex, handler in self._handlers.get(req.method, []):
                    match = path_regex.fullmatch(req.path)
                    if match:
                        req.match = match
                        try:
                            if inspect.iscoroutinefunction(handler):
                                res = await handler(self.env, req)
                            else:
                                res = handler(self.env, req)
                            if not isinstance(res, Response):
                                res = Response(data=res)
                        except:
                            # Error - log it and return 500
                            traceback.print_exc()
                            res = Response(code=500, reason='Internal Server Error')
                        break

                # No handler - send 404
                if res == None:
                    res = Response(code=404, reason='Not Found')

                # Respond
                await res.write(writer)
                print('{}: {} -> {}'.format(peer, req.path,  res.code))
        except EOFError:
            print('Connection closed from {}'.format(peer))

    def run(self, host='localhost', port=1234):
        # Setup loop
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle, host, port, loop=loop)
        server = loop.run_until_complete(coro)

        # Run the server
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':
    app = Grole()
    serve_static(app, '', '.', True)
    app.run()
