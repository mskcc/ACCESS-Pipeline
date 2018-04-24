import unittest


from


class ListToBed(unittest.TestCase):

    def __init__(self):
        self.test_list = '../test_resources/test_list'
        self.test_list_sorted = '../test_resources/test_list_sorted'
        super.__init__(self)

    def test_list_to_bed(self):

        list_to_bed(self.test_list, './outputs/outFile.bed', True)

        with open('./outputs/outFile.bed', 'r') as bed:

            with open('../expected_results/list_to_bed') as expected:

                assert bed.read() == expected.read()


