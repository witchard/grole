import unittest
import pathlib
from helpers import FakeWriter, a_wait

import grole

class TestHeader(unittest.TestCase):

    def test_header(self):
        res = grole.Response(None, 123, 'foo', {'foo': 'bar'}, 'bar')
        writer = FakeWriter()
        a_wait(res._write(writer))
        for line in writer.data.split(b'\r\n'):
            if line.startswith(b'bar'):
                self.assertEqual(line, b'bar 123 foo')
            elif line.startswith(b'Content-Type'):
                self.assertEqual(line, b'Content-Type: text/plain')
            elif line.startswith(b'Content-Length'):
                self.assertEqual(line, b'Content-Length: 0')
            elif line.startswith(b'foo'):
                self.assertEqual(line, b'foo: bar')
            elif line.startswith(b'Server'):
                self.assertEqual(line, b'Server: grole/' + grole.__version__.encode())
            else:
                if line != b'':
                    self.fail('Extra data: ' + line.decode())

class TestBody(unittest.TestCase):

    def test_headers(self):
        res = grole.ResponseBody(b'foo', content_type='bar')
        hdr = {}
        res._set_headers(hdr)
        self.assertDictEqual(hdr, {'Content-Length': 3,
                                   'Content-Type': 'bar'})

    def test_data(self):
        res = grole.ResponseBody(b'foo', content_type='bar')
        writer = FakeWriter()
        a_wait(res._write(writer))
        self.assertEqual(writer.data, b'foo')

    def test_bytes(self):
        res = grole.Response(b'foo')
        self.assertIsInstance(res.data, grole.ResponseBody)

    def test_string(self):
        res = grole.Response('foo')
        self.assertIsInstance(res.data, grole.ResponseString)

    def test_json(self):
        res = grole.Response(['foo'])
        self.assertIsInstance(res.data, grole.ResponseJSON)

    def test_file(self):
        res = grole.Response(grole.ResponseFile('foo'))
        self.assertIsInstance(res.data, grole.ResponseFile)

class TestString(unittest.TestCase):

    def setUp(self):
        self.res = grole.ResponseString('foo', content_type='bar')

    def test_headers(self):
        hdr = {}
        self.res._set_headers(hdr)
        self.assertDictEqual(hdr, {'Content-Length': 3,
                                   'Content-Type': 'bar'})

    def test_data(self):
        writer = FakeWriter()
        a_wait(self.res._write(writer))
        self.assertEqual(writer.data, b'foo')

class TestJSON(unittest.TestCase):

    def setUp(self):
        self.res = grole.ResponseJSON({'foo': 'bar'}, content_type='baz')

    def test_headers(self):
        hdr = {}
        self.res._set_headers(hdr)
        self.assertDictEqual(hdr, {'Content-Length': 14,
                                   'Content-Type': 'baz'})

    def test_data(self):
        writer = FakeWriter()
        a_wait(self.res._write(writer))
        self.assertEqual(writer.data, b'{"foo": "bar"}')

class TestFile(unittest.TestCase):

    def setUp(self):
        testfile = pathlib.Path(__file__).parents[0] / 'test.dat'
        self.res = grole.ResponseFile(str(testfile), content_type='baz')

    def test_headers(self):
        hdr = {}
        self.res._set_headers(hdr)
        self.assertDictEqual(hdr, {'Transfer-Encoding': 'chunked',
                                   'Content-Type': 'baz'})

    def test_data(self):
        writer = FakeWriter()
        a_wait(self.res._write(writer))
        self.assertEqual(writer.data, b'4\r\nfoo\n\r\n0\r\n\r\n')


class TestAuto(unittest.TestCase):

    def test_empty(self):
        res = grole.Response()
        self.assertTrue(isinstance(res.data, grole.ResponseBody))

    def test_bytes(self):
        res = grole.Response(b'foo')
        self.assertTrue(isinstance(res.data, grole.ResponseBody))
        self.assertEqual(res.data._data, b'foo')
        self.assertEqual(res.data._headers['Content-Type'], 'text/plain')

    def test_str(self):
        res = grole.Response('foo')
        self.assertTrue(isinstance(res.data, grole.ResponseString))
        self.assertEqual(res.data._data, b'foo')
        self.assertEqual(res.data._headers['Content-Type'], 'text/html')

    def test_json(self):
        res = grole.Response({'foo': 'bar'})
        self.assertTrue(isinstance(res.data, grole.ResponseJSON))
        self.assertEqual(res.data._data, b'{"foo": "bar"}')
        self.assertEqual(res.data._headers['Content-Type'], 'application/json')

if __name__ == '__main__':
    unittest.main()
