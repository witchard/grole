import asyncio
import io

a_wait = asyncio.new_event_loop().run_until_complete

class FakeReader():
    def __init__(self, data=b'', eof=False):
        self.io = io.BytesIO(data)
        self.eof = eof

    async def readline(self):
        return self.io.readline()

    async def readexactly(self, n):
        data = self.io.read(n)
        if len(data) != n:
            raise asyncio.IncompleteReadError(data, n)
        return data

    def at_eof(self):
        return self.eof

class FakeWriter():
    def __init__(self):
        self.data = b''

    async def drain(self):
        return

    def write(self, data):
        self.data += data
