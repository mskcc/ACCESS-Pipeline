import os
from setuptools import setup, Command

import version


class CleanCommand(Command):
    """
    Custom clean command to tidy up the project root
    """
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


# Write version info to version.py on setup
version_number = version.expand_()
with open('python_tools/pipeline_kickoff/version.py', 'wb') as f:
    f.write(version_number)

# Todo: need to come up with a better way to retain version info
with open('python_tools/version.py', 'wb') as f:
    f.write(version_number)


def req_file(filename):
    """
    We're using a requirements.txt file so that pyup.io can use this for security checks

    :param filename:
    :return:
    """
    with open(filename) as f:
        content = f.readlines()

    return [x.strip() for x in content]

setup(
    name='access_pipeline',
    version=version.most_recent_tag(),
    description='MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline',
    url='http://github.com/mskcc/ACCESS-Pipeline',
    author='Ian Johnson',
    author_email='johnsoni@mskcc.org',
    license='MIT',
    install_requires=req_file('requirements.txt'),
    classifiers=[
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 2.7',
    ],
    packages = [
        'python_tools',
        'python_tools.pipeline_kickoff',
        'python_tools.workflow_tools',
        'python_tools.workflow_tools.qc',
        'python_tools.test',
        'resources'
    ],
    package_data = {
        '': [
            '**/*.r',
            '**/*.R',
            '**/**/*.r',
            '**/**/*.R',
        ],
        'resources': [
            'resources',
            'resources/*',
            'resources/*/*',
            'resources/**/*',
            '*/*.yaml',
            '*.yaml'
        ]
    },
    entry_points = {
        'console_scripts': [
            # Pipeline Kickoff
            'create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main',
            'create_standard_bam_to_collapsed_qc_inputs = python_tools.pipeline_kickoff.create_standard_bam_to_collapsed_qc_inputs:main',
            'create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main',
            'pipeline_submit = python_tools.pipeline_kickoff.pipeline_submit:main',
            'pipeline_runner = python_tools.pipeline_kickoff.pipeline_runner:main',
            # Workflow Tools
            'list2bed = python_tools.workflow_tools.list2bed:main',
            # Quality Control
            'qc_wrapper = python_tools.workflow_tools.qc.qc_wrapper:main',
            'tables_module = python_tools.workflow_tools.qc.tables_module:main',
            'plot_noise = python_tools.workflow_tools.qc.plot_noise:main',
            'base_quality_plot = python_tools.workflow_tools.qc.base_quality_plot:main',
            'fingerprinting = python_tools.workflow_tools.qc.fingerprinting:main',
            'combine_qc_pdfs = python_tools.workflow_tools.qc.combine_qc_pdfs:main',
            # Postprocessing
            'pipeline_postprocessing = python_tools.workflow_tools.pipeline_postprocessing:main',
            # Test Utilities
            'test_outputs = python_tools.test.test_pipeline_outputs:main',
        ]
    },
    scripts=[
        'python_tools/workflow_tools/qc/r_tools/plots_module.r',
        'python_tools/workflow_tools/qc/r_tools/plots.r',
        'python_tools/workflow_tools/qc/r_tools/util.r',
        'python_tools/workflow_tools/qc/r_tools/constants.r',
        'python_tools/workflow_tools/qc/calculate_noise.sh',
        'python_tools/workflow_tools/qc/make_umi_qc_tables.sh',
        'python_tools/workflow_tools/qc/aggregate_bam_metrics.sh',
    ],
    # include_package_data=True,
    # zip_safe=False,
    cmdclass={
        'clean': CleanCommand,
    }
)
