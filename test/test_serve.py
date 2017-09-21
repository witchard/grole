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

    app.run()


class TestServe(unittest.TestCase):

    def test_simple(self):
        p = multiprocessing.Process(target=simple_server)
        p.start()
        time.sleep(0.1)
        with urllib.request.urlopen('http://localhost:1234') as response:
               html = response.read()
               self.assertEqual(html, b'Hello, World!')
        p.terminate()
