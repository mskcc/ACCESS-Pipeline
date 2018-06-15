import unittest

import util


class Tests(unittest.TestCase):

    def setUp(self):
        pass

    def test_extract_sample_name(self):
        # Shold extract sample name from list
        sample = util.extract_sample_name('M-1234_IGO', ['M-1234', 'M-5585'])
        assert sample == 'M-1234'

        # Should return the longest match
        sample = util.extract_sample_name('I_am_a_sample_name', ['I_am_a', 'I_am_a_sample'])
        assert sample == 'I_am_a_sample'


if __name__ == '__main__':
    unittest.main()
