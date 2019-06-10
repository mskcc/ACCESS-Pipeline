import unittest

from python_tools import util


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

    def test_all_strings_are_substrings(self):
        sample_1 = 'SampleABC'
        sample_2 = 'SampleABCD'
        sample_3 = 'SampleABCDE'

        # Should return True because SampleABCDE is the longest match
        are_substrings = util.all_strings_are_substrings([sample_1, sample_2, sample_3])
        assert are_substrings == True

        sample_1 = 'SampleABC'
        sample_2 = 'SampleABCD'
        sample_3 = 'SampleXABCD'

        # Should return False because SampleXABCD is a totally separate match than the other two
        are_substrings = util.all_strings_are_substrings([sample_1, sample_2, sample_3])
        assert are_substrings == False


if __name__ == '__main__':
    unittest.main()
