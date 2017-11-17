import asyncio
import io

a_wait = asyncio.new_event_loop().run_until_complete

class FakeReader():
    def __init__(self, data=b''):
        self.io = io.BytesIO(data)
        self.len = len(data)

    async def readline(self):
        return self.io.readline()

    async def readexactly(self, n):
        data = self.io.read(n)
        if len(data) != n:
            raise asyncio.IncompleteReadError(data, n)
        return data

    def at_eof(self):
        return self.io.tell() == self.len

class FakeWriter():
    def __init__(self):
        self.data = b''

    async def drain(self):
        return

    def write(self, data):
        self.data += data

    def get_extra_info(self, arg):
        return 'fake'

class ErrorWriter():
    def __init__(self):
        self.closed = False

    async def drain(self):
        return

    def write(self, data):
        raise Exception('Broken')

    def get_extra_info(self, arg):
        return 'fake'

    def close(self):
        self.closed = True
