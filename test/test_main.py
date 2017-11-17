import unittest

import grole

class TestMain(unittest.TestCase):

    def test_launch(self):
        # Success is that it doesn't do anything
        grole.main(['-p', '80'])

    def test_launch2(self):
        # Success is that it doesn't do anything
        grole.main(['-p', '80', '-q'])

    def test_launch3(self):
        # Success is that it doesn't do anything
        grole.main(['-p', '80', '-v'])
