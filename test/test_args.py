import unittest

import grole

class TestArgs(unittest.TestCase):

    def test_defaults(self):
        args = grole.parse_args([])
        self.assertEqual(args.address, 'localhost')
        self.assertEqual(args.port, 1234)
        self.assertEqual(args.directory, '.')
        self.assertEqual(args.noindex, False)

    def test_override(self):
        args = grole.parse_args(['-a', 'foo', '-p', '27', '-d', 'bar', '-n'])
        self.assertEqual(args.address, 'foo')
        self.assertEqual(args.port, 27)
        self.assertEqual(args.directory, 'bar')
        self.assertEqual(args.noindex, True)

