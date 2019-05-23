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

    def test_substring_in_list(self):
        assert util.substring_in_list('asdf', ['asdf', 'asdf2', 'asdf3'])
        assert util.substring_in_list('asdf2', ['asdf', 'asdf2', 'asdf3'])
        assert not util.substring_in_list('asdf', ['asddf', 'asddf2', 'asddf3'])

    def test_substrings_in_list(self):
        assert util.substrings_in_list(['123', '456'], ['123456', 'abc'])
        assert util.substrings_in_list(['123', '234'], ['123456', 'abc'])
        assert not util.substrings_in_list(['123', '567'], ['123456', 'abc'])
        assert not util.substrings_in_list(['123', '4567'], ['123456', 'abc'])


if __name__ == '__main__':
    unittest.main()
