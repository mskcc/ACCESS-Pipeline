import os
import pandas as pd

from cwl_tools.hotspots import tag_hotspots
from python_tools.util import ArgparseMock


def main():
    """
    Test for tag_hotspots module
    """
    output_filename = 'expected.maf'
    mock_args = ArgparseMock({
        'input_maf': 'test.maf',
        'input_txt': 'test_hotspots.maf',
        'output_maf': output_filename
    })
    tag_hotspots.main(mock_args)
    expected = pd.read_csv('expected.maf', sep='\t')
    actual = pd.read_csv(output_filename, sep='\t')
    pd.testing.assert_frame_equal(expected, actual)
    os.unlink(output_filename)


if __name__ == '__main__':
    main()
