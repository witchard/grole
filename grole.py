import asyncio
import socket

class Request:
    """
    Handles a single HTTP request
    """
    def __init__(self, reader):
        """
        Initialise
        """
        self.reader = reader

    async def _init(self):
        """
        Perform initialisation
        Parses HTTP request headers, this needs to be async so we can't do it in
        init.
        """
        start_line = await self._readline()
        self.method, self.location, self.version = start_line.decode().split()
        self.headers = {}
        while True:
            header_raw = await self._readline()
            if header_raw.strip() == b'':
                break
            header = header_raw.decode().split(':', 1)
            self.headers[header[0]] = header[1].strip()

        # TODO implement chunked handling
        self.content_remaining = int(self.headers.get('Content-Length', 0))
        self.body = ''

    async def _readline(self):
        """
        Readline helper
        """
        ret = await self.reader.readline()
        if len(ret) == 0 and self.reader.at_eof():
            raise EOFError()
        return ret

    async def buffer_body(self):
        """
        Bufferes the body of the request into body
        """
        if self.content_remaining > 0:
            try:
                self.body = await self.reader.readexactly(self.content_remaining)
                self.content_remaining = 0
            except asyncio.IncompleteReadError:
                self.content_remaining = 0
                raise EOFError()

async def handle_echo(reader, writer):
    peer = writer.get_extra_info('peername')
    print('New connection from {}'.format(peer))
    try:
        while True:
            req = Request(reader)
            await req._init()
            await req.buffer_body()
            print(req.method, req.location, req.version)
            print(req.headers)
            print(req.body.decode())
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