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


# Uncomment to write version info to version.py on setup
# version = version.expand_()
# with open('python_tools/pipeline_kickoff/version.py', 'wb') as f:
#     f.write(version)


setup(
    name='innovation-pipeline-tools',
    version='0.0.0',
    description='MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline',
    url='http://github.com/mskcc/ACCESS-Pipeline',
    author='Ian Johnson',
    author_email='johnsoni@mskcc.org',
    license='MIT',
    install_requires=[
        'argparse',
        'toil-ionox0[cwl]==0.0.1',
        # These dependencies may need to be explicitly specified,
        # if PyPi gives us ResourceConflict issues:
        # 'cwltest==1.0.20180209171722',
        # 'cwltool==1.0.20180403145700',
        'pandas==0.19.0',
        'xlrd==1.1.0',
        'numpy==1.14.2',
        'pysam==0.14.1',
        'pybedtools==0.7.10',
        'PyPDF2==1.26.0',
        'matplotlib==2.2.2',
        'seaborn==0.8.1',
        'mock==2.0.0'
    ],
    dependency_links=[
        'git://git@github.com/ionox0/toil.git@3.15.0#egg=toil-ionox0[cwl]-0.0.1',
    ],
    packages = ['python_tools', 'python_tools.pipeline_kickoff', 'python_tools.workflow_tools', 'python_tools.workflow_tools.qc'],
    package_data = {'': ['**/*.r', '**/*.R', '**/**/*.r', '**/**/*.R']},
    entry_points = {
        'console_scripts': [
            # Pipeline Kickoff
            'create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main',
            'create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main',
            'pipeline_submit = python_tools.pipeline_kickoff.pipeline_submit:main',
            'pipeline_runner = python_tools.pipeline_kickoff.pipeline_runner:main',
            # Workflow Tools
            'list2bed = python_tools.workflow_tools.list2bed:main',
            # Quality Control
            'qc_wrapper = python_tools.workflow_tools.qc.qc_wrapper:main',
            'tables_module = python_tools.workflow_tools.qc.tables_module:main',
            'plot_noise = python_tools.workflow_tools.qc.plot_noise:main',
            'fingerprinting = python_tools.workflow_tools.qc.fingerprinting_v2:main',
            'combine_qc_pdfs = python_tools.workflow_tools.qc.combine_qc_pdfs:main',
            'gender_check = python_tools.workflow_tools.qc.gender_check:main',
        ]
    },
    scripts=[
        'python_tools/workflow_tools/qc/plots_module.r',
        'python_tools/workflow_tools/qc/calculate_noise.sh',
        'python_tools/workflow_tools/qc/make_umi_qc_tables.sh',
        'python_tools/workflow_tools/qc/aggregate_bam_metrics.sh',
    ],
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'clean': CleanCommand,
    }
)
