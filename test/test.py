import unittest
from python_tools.workflow_tools.qc import qc_wrapper, aggregate_bam_metrics


class Tests(unittest.TestCase):

    def test_agbm(self):
        aggregate_bam_metrics.main()

    def test_qc_wrapper(self):
        qc_wrapper.main()


if __name__ == '__main__':
    unittest.main()
