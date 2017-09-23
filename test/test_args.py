import unittest

import grole

class TestArgs(unittest.TestCase):

    def test_defaults(self):
        args = grole.parse_args([])
        self.assertEqual(args.address, 'localhost')
        self.assertEqual(args.port, 1234)
        self.assertEqual(args.directory, '.')
        self.assertEqual(args.noindex, False)
        self.assertEqual(args.verbose, False)
        self.assertEqual(args.quiet, False)

    def test_override(self):
        args = grole.parse_args(['-a', 'foo', '-p', '27', '-d', 'bar', '-n', '-v'])
        self.assertEqual(args.address, 'foo')
        self.assertEqual(args.port, 27)
        self.assertEqual(args.directory, 'bar')
        self.assertEqual(args.noindex, True)
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.quiet, False)

    def test_error(self):
        try:
            grole.parse_args(['-q', '-v'])
        except SystemExit:
            return
        self.fail('Did not error on mutually exclusive args')
