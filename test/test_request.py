import unittest
from helpers import FakeReader, a_wait

import grole

class TestEncoding(unittest.TestCase):

    def setUp(self):
        self.req = grole.Request()
        self.req.data = b'{"foo": "bar"}'

    def test_body(self):
        self.assertEqual(self.req.body(), '{"foo": "bar"}')

    def test_json(self):
        self.assertEqual(self.req.json(), {'foo': 'bar'})

class TestReading(unittest.TestCase):
    
    def setUp(self):
        self.req = grole.Request()

    def test_readline_returns_data(self):
        reader = FakeReader(b'foo\r\nnope')
        line = a_wait(self.req._readline(reader))
        self.assertEqual(line, b'foo\r\n')

    def test_readline_raises_eof(self):
        reader = FakeReader(b'')
        with self.assertRaises(EOFError):
            line = a_wait(self.req._readline(reader))

    def test_buffer_body_content_len_0(self):
        reader = FakeReader(b'foo')
        self.req.headers = {'Content-Length': 0 }
        self.req.data = b''
        a_wait(self.req._buffer_body(reader))
        self.assertEqual(b'', self.req.data)

    def test_buffer_body_content(self):
        reader = FakeReader(b'foobar')
        self.req.headers = {'Content-Length': 3 }
        self.req.data = b''
        a_wait(self.req._buffer_body(reader))
        self.assertEqual(b'foo', self.req.data)

    def test_buffer_body_not_enough_data(self):
        reader = FakeReader(b'foo')
        self.req.headers = {'Content-Length': 4 }
        self.req.data = b''
        with self.assertRaises(EOFError):
            a_wait(self.req._buffer_body(reader))

    def test_header(self):
        header = b'\r\n'.join([b'GET /foo?bar=baz&spam=eggs&chips HTTP/1.1',
                               b'foo: bar',
                               b'']) + b'\r\n'
        a_wait(self.req._read(FakeReader(header)))
        self.assertEqual(self.req.method, 'GET')
        self.assertEqual(self.req.version, 'HTTP/1.1')
        self.assertEqual(self.req.path, '/foo')
        self.assertEqual(self.req.query, {'bar': 'baz', 'spam': 'eggs', 'chips': None})
        self.assertEqual(self.req.headers, {'foo': 'bar'})
        self.assertEqual(self.req.data, b'')

if __name__ == '__main__':
    unittest.main()
