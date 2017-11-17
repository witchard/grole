import unittest
import pathlib
from helpers import *

import grole

class TestGrole(unittest.TestCase):

    def setUp(self):
        self.app = grole.Grole()

    def test_hello(self):
        @self.app.route('/')
        def hello(env, req):
            return 'Hello, World!'

        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'Hello, World!', data)

    def test_async(self):
        @self.app.route('/')
        async def hello_async(env, req):
            return 'Hello, World!'

        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'Hello, World!', data)

    def test_error(self):
        @self.app.route('/')
        def error(env, req):
            a = []
            return a[1]

        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 500 Internal Server Error', data)

    def test_close_big_error(self):
        @self.app.route('/')
        def error(env, req):
            a = []
            return a[1]

        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = ErrorWriter()
        a_wait(self.app._handle(rd, wr))
        self.assertTrue(wr.closed)


    def test_404(self):
        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()

        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 404 Not Found', data)

class TestStatic(unittest.TestCase):

    def setUp(self):
        self.app = grole.Grole()

    def test_file(self):
        testfolder = str(pathlib.Path(__file__).parents[0])
        grole.serve_static(self.app, '', testfolder, index=False)
        rd = FakeReader(data=b'GET /test.dat HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'4\r\nfoo\n\r\n0', data)

    def test_index(self):
        testfolder = str(pathlib.Path(__file__).parents[0])
        grole.serve_static(self.app, '', testfolder, index=True)
        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 200 OK', data)

    def test_index2(self):
        testfolder = str(pathlib.Path(__file__).parents[1])
        grole.serve_static(self.app, '', testfolder, index=True)
        rd = FakeReader(data=b'GET /test HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 200 OK', data)

    def test_notfound(self):
        testfolder = str(pathlib.Path(__file__).parents[0])
        grole.serve_static(self.app, '', testfolder, index=False)
        rd = FakeReader(data=b'GET /foo HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 404 Not Found', data)

class TestDoc(unittest.TestCase):

    def setUp(self):
        self.app = grole.Grole()

    def test_doc(self):
        @self.app.route('/hello')
        def hello(env, req):
            return 'Hello, World!'

        grole.serve_doc(self.app, '/')
        rd = FakeReader(data=b'GET / HTTP/1.1\r\n\r\n')
        wr = FakeWriter()
        a_wait(self.app._handle(rd, wr))
        data = wr.data.split(b'\r\n')[0]
        self.assertEqual(b'HTTP/1.1 200 OK', data)

if __name__ == '__main__':
    unittest.main()
