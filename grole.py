"""
Grole is a simple asyncio based web framework
"""
import asyncio
import socket
import json
import re
import traceback
import inspect
from collections import defaultdict


class Request:
    """
    Represents a single HTTP request

    The read method parses a request. The following members are filled in
    with the details:
      method   The request method
      location The request location / path
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
    def __init__(self, data=b''):
        """
        Initialise object, data is the data to send
        """
        self._headers = {'Content-Length': len(data),
                         'Content-Type': 'text/plain'}
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
    def __init__(self, data=''):
        super().__init__(data.encode())

class ResponseJSON(ResponseString):
    """
    Response body encoded in json
    """
    def __init__(self, data=''):
        super().__init__(json.dumps(data))
        self._headers['Content-Type'] = 'application/json'

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
        self.headers = {'Server': 'grole/0.1'}
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

class Grole:
    """
    A Grole Webserver
    """
    def __init__(self, env=None):
        self._handlers = defaultdict(list)
        self.env = env

    def route(self, path_regex, methods=['GET']):
        """
        Decorator to register a handler

        For example:
        app = Grole()
        @app.route('/')
        def index(env, req):
          return 'Hello, World!'
        app.run()
        """
        def register_func(func):
            """
            Decorator implementation
            """
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
                    match = path_regex.fullmatch(req.location)
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
                print('{}: {} -> {}'.format(peer, req.location,  res.code))
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
    app.env = {'message': 'Hello, World!'}

    @app.route('/(\d+)')
    def index(env, req):
        times = int(req.match.group(1))
        return {'result': env['message']*times, 'times': times}

    @app.route('/message', methods=['POST'])
    def update(env, req):
        env['message'] = req.body()

    
    @app.route('/sleep')
    async def sleep(env, req):
        await asyncio.sleep(2)

    app.run()
