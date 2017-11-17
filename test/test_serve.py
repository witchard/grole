import unittest
import asyncio
import io
import multiprocessing
import urllib.request
import time

import grole

def simple_server():
    app = grole.Grole()

    @app.route('/')
    def hello(env, req):
        return 'Hello, World!'

    app.run(host='127.0.0.1')

class TestServe(unittest.TestCase):

    def test_simple(self):
        p = multiprocessing.Process(target=simple_server)
        p.start()
        time.sleep(0.1)
        with urllib.request.urlopen('http://127.0.0.1:1234') as response:
               html = response.read()
               self.assertEqual(html, b'Hello, World!')
        p.terminate()

    def test_fileserver(self):
        p = multiprocessing.Process(target=grole.main, args=[['-a', '127.0.0.1']])
        p.start()
        time.sleep(0.1)
        with urllib.request.urlopen('http://127.0.0.1:1234/test/test.dat') as response:
               html = response.read()
               self.assertEqual(html, b'foo\n')
        p.terminate()

    def test_https(self):
        p = multiprocessing.Process(target=simple_server)
        p.start()
        time.sleep(0.1)
        self.assertRaises(urllib.error.URLError)
        p.terminate()


