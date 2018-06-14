import sys
import unittest
from mock import patch


class Tests(unittest.TestCase):

    def setUp(self):
        self._test_args = [
            'aggregate_bam_metrics.py',
            'python_tools/test/test_data/waltz_output',
            'python_tools/test/test_data/test_title_file.txt'
        ]

    def test_process_read_counts_files(self):

        with patch.object(sys, 'argv', self._test_args):

            from python_tools.workflow_tools.qc import aggregate_bam_metrics

            aggregate_bam_metrics.main()


if __name__ == '__main__':
    unittest.main()
