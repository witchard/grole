import asyncio
import socket
import json

class Request:
    """
    Handles a single HTTP request
    """
    async def _init(self, reader):
        """
        Perform initialisation - Parses HTTP request headers and body
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
        self.data = ''
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
        Decodes body as string - must be called after buffer_body
        """
        return self.data.decode()

    def json(self):
        """
        Decodes json object from the body - must be called after buffer_body
        """
        return json.loads(self.body())

async def handle_echo(reader, writer):
    peer = writer.get_extra_info('peername')
    print('New connection from {}'.format(peer))
    try:
        while True:
            req = Request()
            await req._init(reader)
            print(req.method, req.location, req.version)
            print(req.headers)
            print(req.json())
            writer.write(b'HTTP/1.1 404 Not Found\r\nServer: grole/0.1\r\nContent-Length: 0\r\n\r\n')
            await writer.drain()
            print('Handled request')
    except EOFError:
        print('Connection closed from {}'.format(peer))


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, 'localhost', 1234, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print(socket.gethostname())
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()