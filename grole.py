import asyncio
import socket
import pprint

async def get_header(reader):
    start_line = await reader.readline()
    method, location, version = start_line.decode().split()
    headers = {}
    while True:
        header_raw = await reader.readline()
        if header_raw.strip() == b'':
            break
        header = header_raw.decode().split(':', 1)
        headers[header[0]] = header[1].strip()
    return {'method': method, 'location': location, 'version': version,
            'headers': headers}

async def handle_echo(reader, writer):
    print("New connection from {}".format(writer.get_extra_info('peername')))
    while True:
        req = await get_header(reader)
        pprint.pprint(req)
        writer.write(b'HTTP/1.1 404 Not Found\r\nServer: grole/0.1\r\nContent-Length: 0\r\n\r\n')
        await writer.drain()
        print('Handled request')


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